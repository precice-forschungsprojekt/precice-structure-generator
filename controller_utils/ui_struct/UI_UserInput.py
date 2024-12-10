from controller_utils.ui_struct.UI_SimulationInfo import UI_SimulationInfo
from controller_utils.ui_struct.UI_Participant import UI_Participant
from controller_utils.ui_struct.UI_Coupling import UI_Coupling
from controller_utils.myutils.UT_PCErrorLogging import UT_PCErrorLogging

class UI_UserInput(object):
    """
    This class represents the main object that contains either one YAML file
    or a user input through a GUI

    The main components are:
     - the list of participants
     - general simulation informations
    """
    def __init__(self):
        """The constructor, dummy initialization of the fields"""
        self.sim_info = UI_SimulationInfo()
        self.participants = {} # empty participants stored as a dictionary
        self.couplings = []    # empty coupling list
        pass

    def init_from_yaml(self, etree, mylog: UT_PCErrorLogging):
        """ this method initializes all fields from a parsed YAML file
         we assume that the YAML file has already has been parsed and we get
         as input the root node of the file
        """
        #todo catch the exceptions here

        # build the simulation info
        simulation_info = etree["simulation"]
        self.sim_info.init_from_yaml(simulation_info, mylog)

        # build all the participants
        participants_list = etree["participants"]
        for participant_name in participants_list:
            participant_data = participants_list[participant_name]
            new_participant = UI_Participant()
            new_participant.init_from_yaml(participant_data, participant_name, mylog)
            # add the participant to the dictionary
            self.participants[participant_name] = new_participant
            pass

        # build the couplings
        couplings_list = etree["couplings"]
        for couplings in couplings_list:
            # new coupling structure of the couplig section
            # print("coupling name:", couplings)
            # this will be only one loop always due to the YAML structure
            for coupling_name in couplings:
                # print("coupling type = ", coupling_name)
                coupling_data = couplings[coupling_name]
                # print("coupling data =",coupling_data)
                new_coupling = UI_Coupling()
                new_coupling.init_from_yaml(coupling_name, coupling_data, self.participants, mylog)
                # add the coupling to the list of couplings
                self.couplings.append(new_coupling)


        # mylog.rep_info("End building user input")
        # build the list of participants

        pass