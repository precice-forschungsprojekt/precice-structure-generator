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
        simulation_info = etree["coupling-scheme"]

        # Extract additional parameters
        sync_mode = simulation_info.get("sync-mode", "on")  # Default: "on"
        mode = simulation_info.get("mode", "fundamental")   # Default: "fundamental"
        self.sim_info.sync_mode = sync_mode
        self.sim_info.mode = mode

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

        # build the couplings from exchanges
        # If exchanges exist, use them; otherwise fall back to couplings
        if "exchanges" in etree:
            exchanges_list = etree["exchanges"]
            for exchange in exchanges_list:
                new_coupling = UI_Coupling()
                # Create a coupling from the exchange information
                coupling_data = {
                    "from": exchange["from"],
                    "to": exchange["to"],
                    "data": exchange["data"],
                    "type": exchange.get("type", "strong")
                }
                new_coupling.init_from_yaml("fsi", coupling_data, self.participants, mylog)
                # add the coupling to the list of couplings
                self.couplings.append(new_coupling)
        elif "couplings" in etree:
            # Existing code for backward compatibility
            couplings_list = etree["couplings"]
            for couplings in couplings_list:
                for coupling_name in couplings:
                    coupling_data = couplings[coupling_name]
                    new_coupling = UI_Coupling()
                    new_coupling.init_from_yaml(coupling_name, coupling_data, self.participants, mylog)
                    # add the coupling to the list of couplings
                    self.couplings.append(new_coupling)
        else:
            mylog.rep_error("No exchanges or couplings found in the topology file")

        pass