from controller_utils.myutils.UT_PCErrorLogging import UT_PCErrorLogging
from controller_utils.precice_struct.PS_ParticipantSolver import PS_ParticipantSolver
from controller_utils.ui_struct.UI_UserInput import UI_UserInput
from controller_utils.ui_struct.UI_Coupling import UI_CouplingType
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
                i = etree.SubElement(coupling_scheme, "participant", first=mylist[0],
                                     second=mylist[1])
            else:
                i = etree.SubElement(coupling_scheme, "participant", first=mylist[1],
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
                    i = etree.SubElement(coupling_scheme, "participant", name=participant_name, control="yes")
                else:
                    i = etree.SubElement(coupling_scheme, "participant", name=participant_name)
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
            #print(" solver=", solver, " q=", q.name, " i=", q.instance_name, " v=", solver.solver_domain.value)
            if solver_simplicity < solver.solver_domain.value:
                simple_solver = solver
                pass
            pass
        # For each quantity we specify the exchange and the convergence
        for q_name in config.coupling_quantities:
            q = config.coupling_quantities[q_name]
            solver = q.source_solver

            # look for the second solver in the list of solver within the quantity
            # there should be only two solvers in this list!
            other_solver_for_coupling = None
            other_mesh_name = "None" # if we heed the other mesh name not the "real" source
            for oq in q.list_of_solvers:
                other_solver = q.list_of_solvers[oq]
                if other_solver.name != solver.name:
                    other_solver_for_coupling = other_solver
                    for allm in other_solver.meshes:
                        if allm != q.source_mesh_name:
                            other_mesh_name = allm

            # the from and to attributes
            from_s = "___"
            to_s = "__"
            exchange_mesh_name = q.source_mesh_name
            if solver.name != simple_solver.name:
                from_s = solver.name
                to_s = simple_solver.name
                exchange_mesh_name = other_mesh_name
            else:
                from_s = solver.name
                to_s = other_solver_for_coupling.name

            # TODO: the mesh must be the coupled mesh that both participant have
            # print (" size =" , len( q.list_of_solvers ) )
            e = etree.SubElement(coupling_scheme, "exchange", data=q_name, mesh=exchange_mesh_name
                                 ,from___ = from_s, to=to_s)
            # TODO: here the oposite from above
            if relative_conv_str != "":
                c = etree.SubElement(coupling_scheme, "relative-convergence-measure",
                                 limit=relative_conv_str, mesh=exchange_mesh_name
                                 ,data=q_name)
            pass


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

        i = etree.SubElement(coupling_scheme, "max-time-windows", value=str(self.NrTimeStep))
        attr = { "value": str(self.Dt),   "valid-digits": "8"}
        i = etree.SubElement(coupling_scheme, "time-window-size", attr)

        # write out the exchange but not the convergence (if empty it will not be written)
        self.write_exchange_and_convergance(config, coupling_scheme, "")


class PS_ImplicitCoupling(PS_CouplingScheme):
    """ Implicit coupling scheme """
    def __init__(self):

        # TODO: define here only implicit coupling specific measures

        self.NrTimeStep = -1
        self.Dt = 1E-4
        self.maxIteration = 100
        self.relativeConverganceEps = 1E-4
        self.extrapolation_order = 2
        self.acceleration = PS_ImplicitAcceleration() # this is the postprocessing
        pass

    def initFromUI(self, ui_config:UI_UserInput, conf): # conf : PS_PreCICEConfig
        # call theinitialization from the UI data structures
        super(PS_ImplicitCoupling, self).init_from_UI(ui_config, conf)

        # Configure acceleration based on coupling type and user preferences
        # By default, use IQN-ILS for strong interactions
        self.acceleration.type = "IQN-ILS"
        
        # Configure primary data based on coupling quantities
        for q_name, q in conf.coupling_quantities.items():
            # Assume the first quantity as primary data
            if not self.acceleration.primary_data:
                self.acceleration.primary_data[q.instance_name] = q.source_mesh_name
            else:
                # Additional quantities as secondary data
                self.acceleration.secondary_data[q.instance_name] = q.source_mesh_name

        # Adjust acceleration parameters based on simulation characteristics
        simulation_conf = ui_config.sim_info
        
        # Determine acceleration type based on number of coupling quantities and coupling type
        num_coupling_quantities = len(conf.coupling_quantities)
        
        # For multiple coupling quantities or complex coupling types, use more advanced acceleration
        if num_coupling_quantities > 2 or any(c.coupling_type in [UI_CouplingType.fsi, UI_CouplingType.cht] for c in ui_config.couplings):
            self.acceleration.type = "IQN-IMVJ"
            self.acceleration.time_windows_reused = 10
            self.acceleration.filter_limit = 1e-2
        
        # For simple, less coupled simulations, use constant or Aitken
        elif num_coupling_quantities <= 1:
            self.acceleration.type = "constant"
            self.acceleration.relaxation_value = 0.5
        
        # Set common parameters
        self.acceleration.initial_relaxation_qn = 0.1
        self.acceleration.max_used_iterations = 100

        # Store other simulation parameters
        self.NrTimeStep = simulation_conf.NrTimeStep
        self.Dt = simulation_conf.Dt

        pass

    def write_precice_xml_config(self, tag:etree, config): # config: PS_PreCICEConfig
        """ write out the config XMl file """
        coupling_scheme = self.write_participants_and_coupling_scheme( tag, config, "parallel-implicit" )

        i = etree.SubElement(coupling_scheme, "max-time-windows", value = str(self.NrTimeStep))
        attr = { "value": str(self.Dt),   "valid-digits": "8"}
        i = etree.SubElement(coupling_scheme, "time-window-size", attr)
        i = etree.SubElement(coupling_scheme, "max-iterations", value=str(self.maxIteration))
        #i = etree.SubElement(coupling_scheme, "extrapolation-order", value=str(self.extrapolation_order))

        # write out the exchange and the convergance rate
        self.write_exchange_and_convergance(config, coupling_scheme, str(self.relativeConverganceEps))

        # finally we write out the acceleration...
        self.acceleration.write_precice_xml_config(coupling_scheme, config, self)

        pass


class PS_ImplicitAcceleration(object):
    """ class to model the acceleration part of the implicit coupling """
    def __init__(self):
        """ Ctor for the acceleration """
        # Acceleration type options: 'constant', 'aitken', 'IQN-ILS', 'IQN-IMVJ'
        self.type = "constant"
        
        # Constant under-relaxation parameters
        self.relaxation_value = 0.5
        
        # Aitken under-relaxation parameters
        self.initial_relaxation = 0.1
        
        # Quasi-Newton parameters (IQN-ILS and IQN-IMVJ)
        self.preconditioner_type = "residual-sum"
        self.filter_type = "QR2"
        self.filter_limit = 1e-3
        self.initial_relaxation_qn = 0.1
        self.max_used_iterations = 100
        self.time_windows_reused = 20
        
        # Primary and secondary data
        self.primary_data = {}
        self.secondary_data = {}
        
        pass

    def write_precice_xml_config(self, coupling_scheme, config, implicit_coupling):
        """ write out the acceleration configuration """
        # Check if we have any quantities to accelerate
        if len(self.primary_data) > 0 or len(self.secondary_data) > 0:
            # Create acceleration tag based on type
            if self.type == "constant":
                acceleration_tag = etree.SubElement(coupling_scheme, "acceleration:constant")
                etree.SubElement(acceleration_tag, "relaxation", value=str(self.relaxation_value))
            
            elif self.type == "aitken":
                acceleration_tag = etree.SubElement(coupling_scheme, "acceleration:aitken")
                # Add primary data
                for data_name, mesh_name in self.primary_data.items():
                    etree.SubElement(acceleration_tag, "data", name=data_name, mesh=mesh_name)
                etree.SubElement(acceleration_tag, "initial-relaxation", value=str(self.initial_relaxation))
            
            elif self.type in ["IQN-ILS", "IQN-IMVJ"]:
                acceleration_tag = etree.SubElement(coupling_scheme, f"acceleration:{self.type}")
                
                # Add primary data
                for data_name, mesh_name in self.primary_data.items():
                    etree.SubElement(acceleration_tag, "data", name=data_name, mesh=mesh_name)
                
                # Add preconditioner
                etree.SubElement(acceleration_tag, "preconditioner", type=self.preconditioner_type)
                
                # Add filter
                etree.SubElement(acceleration_tag, "filter", type=self.filter_type, limit=str(self.filter_limit))
                
                # Add initial relaxation
                etree.SubElement(acceleration_tag, "initial-relaxation", value=str(self.initial_relaxation_qn))
                
                # Add max used iterations and time windows reused
                etree.SubElement(acceleration_tag, "max-used-iterations", value=str(self.max_used_iterations))
                etree.SubElement(acceleration_tag, "time-windows-reused", value=str(self.time_windows_reused))
            
            pass
