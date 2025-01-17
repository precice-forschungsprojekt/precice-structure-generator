from controller_utils.myutils.UT_PCErrorLogging import UT_PCErrorLogging
from enum import Enum

class UI_CouplingType(Enum):
    """ enum type to represent the different coupling types"""
    fsi = 0
    cht = 1
    f2s = 2
    error_coupling = -1

class UI_Coupling(object):
    """
    This class contains information on the user input level
    regarding the coupling of two participants
    """
    def __init__(self):
        """The constructor."""
        self.boundaryC1 = -1
        self.boundaryC2 = -1
        self.partitcipant1 = None
        self.partitcipant2 = None
        self.coupling_type = UI_CouplingType.error_coupling
        pass

    def init_from_yaml(self, name_coupling: str, etree, participants: dict,
                       mylog: UT_PCErrorLogging):
        """ Method to initialize fields from a parsed YAML file node """

        # new coupling info
        # name of the coupling is the type "fsi" or "chi"

        if name_coupling == "fsi":
            # fsi coupling, meaning we have "fluid" and "structure", implicit coupling
            self.coupling_type = UI_CouplingType.fsi
        elif name_coupling == "f2s":
            # fsi coupling, meaning we have "fluid" and "structure", explicit coupling
            self.coupling_type = UI_CouplingType.f2s
        elif name_coupling == "cht":
            # conjugate heat transfer -> there we also have fluid and structure
            self.coupling_type = UI_CouplingType.cht
        else:
            # Throw an error
            mylog.rep_error("Unknown coupling type:" + name_coupling)

        # parse all the participants within a coupling
        try:
            # Check if this is an old-style coupling or a new exchanges-style coupling
            if "fluid" in etree and "structure" in etree:
                # Old-style coupling format
                participants_loop = { "fluid" : etree["fluid"]}
                participants_loop.update({ "structure" : etree["structure"] } )
            else:
                # New exchanges-style format
                participants_loop = {
                    "from": {"name": etree["from"], "interface": etree.get("from-patch", "interface")},
                    "to": {"name": etree["to"], "interface": etree.get("to-patch", "interface")}
                }

            # VERY IMPORTANT: we sort here the keys alphabetically!!!
            # this is an important assumption also in other parts of the code, that the participant1
            # and participant2 are in alphabetical order. example 1) fluid 2) structure at fsi
            sorted_keys = sorted(participants_loop.keys())
            for participant_name in sorted_keys:
                participant = participants_loop[participant_name]
                
                # Handle both old and new format
                if isinstance(participant, dict):
                    participant_real_name = participant["name"]
                    participant_interface = participant["interface"]
                else:
                    participant_real_name = participant
                    participant_interface = "interface"  # default interface

                partitcip = participants[participant_real_name]
                partitcip.solver_domain = participant_name # this might be fluid or structure or something else
                # add only to the first participant the coupling
                partitcip.list_of_couplings.append(self)
                # now link this to one of the participants
                if self.partitcipant1 == None:
                    self.partitcipant1 = partitcip
                    self.boundaryC1 = participant_interface
                else:
                    self.partitcipant2 = partitcip
                    self.boundaryC2 = participant_interface

        except Exception as e:
            mylog.rep_error(f"Error in YAML initialization of the Coupling name={name_coupling} data: {str(e)}")
        pass

    def get_first_boundary_code(self, solverName: str):
        """Returns the first boundary code with respect to the solver name """
        if solverName == self.partitcipant1.name:
            return self.boundaryC1
        return self.boundaryC2

    def get_second_boundary_code(self, solverName: str):
        """Returns the second boundary code with respect to the solver name """
        if solverName != self.partitcipant1.name:
            return self.boundaryC1
        return self.boundaryC2
