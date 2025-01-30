from controller_utils.myutils.UT_PCErrorLogging import UT_PCErrorLogging
from controller_utils.precice_struct.PS_ParticipantSolver import PS_ParticipantSolver
from controller_utils.ui_struct.UI_UserInput import UI_UserInput
import xml.etree.ElementTree as etree

class PS_CouplingScheme(object):
    """Class to represent the Coupling schemes """
    def __init__(self):
        """Ctor to initialize all the fields """
        self.firstSolver = None
        self.secondSolver = None
        pass

    def init_from_UI(self, ui_config:UI_UserInput, conf): # : PS_PreCICEConfig
        """ This method should be overwritten by the subclasses """
        pass

    def write_precice_xml_config(self, tag: etree, config): # config: PS_PreCICEConfig
        """ parent function to write out XML file """
        pass

    def write_participants_and_coupling_scheme(self, tag: etree, config, coupling_str:str ):
        """ write out the config XMl file """
        if len(config.solvers) <= 2:
            # for only
            coupling_scheme = etree.SubElement(tag, "coupling-scheme:" + coupling_str)
            # print the participants, ASSUMPTION! we assume there is at least two
            mylist = ["NONE", "NONE"]
            mycomplexity = [-1, -1]
            myindex = 0
            for participant_name in config.solvers:
                p = config.solvers[participant_name]
                mylist[myindex] = participant_name
                mycomplexity[myindex] = p.solver_domain.value
                myindex = myindex + 1
                pass
            # the solver with the higher complexity should be first
            if mycomplexity[0] < mycomplexity[1]:
                i = etree.SubElement(coupling_scheme, "participants", first=mylist[0],
                                     second=mylist[1])
            else:
                i = etree.SubElement(coupling_scheme, "participants", first=mylist[1],
                                     second=mylist[0])
        else:
            # TODO: is "multi" good for all
            coupling_scheme = etree.SubElement(tag, "coupling-scheme:multi")
            # first find the solver with the most meshes and this should be the one who controls the coupling
            nr_max_meshes = -1
            control_participant_name = "NONE"
            for participant_name in config.solvers:
                participant = config.solvers[participant_name]
                # TODO: we should select the solver with the most meshes ?
                if len(participant.meshes) > nr_max_meshes:
                    nr_max_meshes = len(participant.meshes)
                    control_participant_name = participant.name
                pass
            # second print all the participants
            for participant_name in config.solvers:
                participant = config.solvers[participant_name]
                if participant.name == control_participant_name:
                    i = etree.SubElement(coupling_scheme, "participants", name=participant_name, control="yes")
                else:
                    i = etree.SubElement(coupling_scheme, "participants", name=participant_name)
                    pass
                pass
            pass
        return coupling_scheme

    def write_exchange_and_convergance(self, config, coupling_scheme, relative_conv_str:str):
        """ Writes to the XML the exchange list """
        # select the solver with minimal complexity
        simple_solver = None
        solver_simplicity = -2
        for q_name in config.coupling_quantities:
            q = config.coupling_quantities[q_name]
            solver = q.source_solver
            if solver_simplicity < solver.solver_domain.value:
                simple_solver = solver

        # For each quantity, specify the exchange and the convergence
        for q_name in config.coupling_quantities:
            q = config.coupling_quantities[q_name]
            solver = q.source_solver

            # look for the second solver in the list of solvers within the quantity
            other_solver_for_coupling = None
            other_mesh_name = None  # Initialize other mesh name
            for oq in q.list_of_solvers:
                other_solver = q.list_of_solvers[oq]
                if other_solver.name != solver.name:
                    other_solver_for_coupling = other_solver
                    for allm in other_solver.meshes:
                        if allm != q.source_mesh_name:
                            other_mesh_name = allm

            # the from and to attributes
            from_s = solver.name
            to_s = other_solver_for_coupling.name
            exchange_mesh_name = other_mesh_name if solver.name == simple_solver.name else q.source_mesh_name

            e = etree.SubElement(coupling_scheme, "exchange", data=q_name, mesh=exchange_mesh_name,
                                from___=from_s, to=to_s)

            if relative_conv_str != "":
                c = etree.SubElement(coupling_scheme, "relative-convergence-measure",
                                    limit=relative_conv_str, mesh=exchange_mesh_name, data=q_name)


class PS_ExplicitCoupling(PS_CouplingScheme):
    """ Explicit coupling scheme """
    def __init__(self):
        self.NrTimeStep = -1
        self.Dt = 1E-4
        pass

    def initFromUI(self, ui_config: UI_UserInput, conf):  # conf : PS_PreCICEConfig
        # call theinitialization from the UI data structures
        super(PS_ExplicitCoupling, self).init_from_UI(ui_config, conf)
        simulation_conf = ui_config.sim_info
        self.NrTimeStep = simulation_conf.NrTimeStep
        self.Dt = simulation_conf.Dt
        pass

    def write_precice_xml_config(self, tag:etree, config): # config: PS_PreCICEConfig
        """ write out the config XMl file """
        coupling_scheme = self.write_participants_and_coupling_scheme( tag, config, "parallel-explicit" )

        i = etree.SubElement(coupling_scheme, "max-time", value=str(self.NrTimeStep))
        attr = { "value": str(self.Dt)}
        i = etree.SubElement(coupling_scheme, "time-window-size", attr)

        # write out the exchange but not the convergence (if empty it will not be written)
        self.write_exchange_and_convergance(config, coupling_scheme, "")


class PS_ImplicitCoupling(PS_CouplingScheme):
    """ Implicit coupling scheme """
    def __init__(self):

        # TODO: define here only implicit coupling specific measures

        self.NrTimeStep = -1
        self.Dt = 1E-4
        self.maxIteration = 50
        self.relativeConverganceEps = 1E-4
        self.extrapolation_order = 2
        self.postProcessing = PS_ImplicitPostPropocessing() # this is the postprocessing
        pass

    def initFromUI(self, ui_config:UI_UserInput, conf): # conf : PS_PreCICEConfig
        # call theinitialization from the UI data structures
        super(PS_ImplicitCoupling, self).init_from_UI(ui_config, conf)

        # TODO: should we add all quantities?
        # later do delte some quantities from the list?
        self.postProcessing.post_process_quantities = conf.coupling_quantities

        simulation_conf = ui_config.sim_info

        self.NrTimeStep = simulation_conf.NrTimeStep
        self.Dt = simulation_conf.Dt

        pass

    def write_precice_xml_config(self, tag:etree, config): # config: PS_PreCICEConfig
        """ write out the config XMl file """
        coupling_scheme = self.write_participants_and_coupling_scheme( tag, config, "parallel-implicit" )

        i = etree.SubElement(coupling_scheme, "max-time", value = str(self.NrTimeStep))
        attr = { "value": str(self.Dt)}
        i = etree.SubElement(coupling_scheme, "time-window-size", attr)
        i = etree.SubElement(coupling_scheme, "max-iterations", value=str(self.maxIteration))
        #i = etree.SubElement(coupling_scheme, "extrapolation-order", value=str(self.extrapolation_order))

        # write out the exchange and the convergance rate
        self.write_exchange_and_convergance(config, coupling_scheme, str(self.relativeConverganceEps))

        # finally we write out the post processing...
        self.postProcessing.write_precice_xml_config(coupling_scheme, config, self)

        pass


class PS_ImplicitPostPropocessing(object):
    """ Class to model the post-processing part of the implicit coupling """
    def __init__(self):
        """ Ctor for the postprocessing """
        self.name = "IQN-ILS"
        self.precondition_type = "residual-sum"
        self.post_process_quantities = {} # The quantities that are in the acceleration

    def write_precice_xml_config(self, tag: etree.Element, config, parent):
        """ Write out the config XML file of the acceleration in case of implicit coupling
            Only for explicit coupling (one directional) this should not write out anything """

        post_processing = etree.SubElement(tag, "acceleration:" + self.name)

        # Find the solver with the minimal complexity (assuming it's the solid solver)
        simple_solver = None
        solver_simplicity = -2
        for q_name in config.coupling_quantities:
            q = config.coupling_quantities[q_name]
            solver = q.source_solver
            if solver_simplicity < solver.solver_domain.value:
                simple_solver = solver

        solid_mesh_name = None
        for q_name in config.coupling_quantities:
            q = config.coupling_quantities[q_name]
            solver = q.source_solver

            # Determine the mesh name dynamically
            mesh_name = q.source_mesh_name
            for oq in q.list_of_solvers:
                other_solver = q.list_of_solvers[oq]
                if other_solver.name != solver.name and other_solver.name == simple_solver.name:
                    for other_mesh in other_solver.meshes:
                        if other_mesh != q.source_mesh_name:
                            mesh_name = other_mesh
                            solid_mesh_name = mesh_name
                            break

            if not solid_mesh_name:
                solid_mesh_name = mesh_name  # fallback if no other mesh found

            i = etree.SubElement(post_processing, "data", name=q.instance_name, mesh=solid_mesh_name)
