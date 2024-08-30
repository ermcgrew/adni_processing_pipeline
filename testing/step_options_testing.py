## based on files required for each stats category
ashst1steps=["neck_trim", "t1icv", "superres", "t1ashs", "t1mtthk", "ashst1_stats"]
ashst2steps=["neck_trim", "t2ashs", "prc_cleanup", "ashst2_stats"]
structuresteps=["neck_trim", "cortical_thick", "brain_ex", "whole_brain_seg", "wbseg_to_ants", 
                "pmtau", "structure_stats"]
wmhsteps=["flair_skull_strip", "wmh_seg", "wmh_stats"]
petsteps=["neck_trim", "cortical_thick", "brain_ex", "whole_brain_seg", "wbseg_to_ants", 
            "inf_cereb_mask", "t1icv", "superres", "t1ashs", "t2ashs", "prc_cleanup", 
            "t1_pet_reg", "t1_pet_suvr", "pet_stats"]  

test_steps_dict={"neck_trim":"neck_trim", "cortical_thick":"cortical_thick", "brain_ex":"brain_ex", 
                "whole_brain_seg":"whole_brain_seg", "wbseg_to_ants":"wbseg_to_ants", 
                "wbsegqc":"wbsegqc", "inf_cereb_mask":"inf_cereb_mask", "pmtau":"pmtau", 
                "t1icv":"t1icv", "superres":"superres", "t1ashs":"t1ashs", "t1mtthk":"t1mtthk", 
                "t2ashs":"t2ashs", "prc_cleanup":"prc_cleanup", 
                "flair_skull_strip":"flair_skull_strip", "wmh_seg":"wmh_seg",
                "t1_pet_reg":"t1_pet_reg", "t1_pet_suvr":"t1_pet_suvr", "pet_reg_qc":"pet_reg_qc",
                "ashst1_stats":"ashst1_stats", "ashst2_stats":"ashst2_stats", "wmh_stats":"wmh_stats",
                "structure_stats":"structure_stats", "pet_stats":"pet_stats", 
                "ashst1steps":["neck_trim", "t1icv", "superres", "t1ashs", "t1mtthk", "ashst1_stats"],
                "ashst2steps":["neck_trim", "t2ashs", "prc_cleanup", "ashst2_stats"],
                "structuresteps":["neck_trim", "cortical_thick", "brain_ex", "whole_brain_seg", "wbseg_to_ants", 
                                "pmtau", "structure_stats"],
                "wmhsteps":["flair_skull_strip", "wmh_seg", "wmh_stats"],
                "petsteps":["neck_trim", "cortical_thick", "brain_ex", "whole_brain_seg", "wbseg_to_ants", 
                            "inf_cereb_mask", "t1icv", "superres", "t1ashs", "t2ashs", "prc_cleanup", 
                            "t1_pet_reg", "t1_pet_suvr", "pet_stats"]  
    }
