#!/usr/bin/env python3


all_steps=["neck_trim", "cortical_thick", "brain_ex", "whole_brain_seg", "wbseg_to_ants", 
            "wbsegqc", "inf_cereb_mask", "pmtau", 
            "t1icv", "superres","t1ashs", "t1mtthk", "t2ashs", "prc_cleanup", 
            "flair_skull_strip", 
            "t1_pet_reg", "t1_pet_suvr", "pet_reg_qc",
            "ashst1_stats", "ashst2_stats", "wmh_stats", "structure_stats", "pet_stats"]


def determine_parent_step(step_to_do):
    if step_to_do == "neck_trim":
        # print('first step, no parent job')
        return []
    elif step_to_do == "cortical_thick" or step_to_do == "brain_ex" or step_to_do == "t1icv" \
        or step_to_do == "superres" or step_to_do == "t2ashs" or step_to_do == "t1_pet_reg":
        return ["neck_trim"]
    elif step_to_do == "whole_brain_seg":
        return ["brain_ex"]
    elif step_to_do == "wbseg_to_ants":
        return ["whole_brain_seg", "cortical_thick"]
    elif step_to_do == "wbsegqc" or step_to_do == "inf_cereb_mask":
        return ["whole_brain_seg"]
    elif step_to_do == "t1ashs":
        return ["superres"]
    elif step_to_do == "t1mtthk":
        return ["t1ashs"]
    elif step_to_do == "prc_cleanup":
        return ["t2ashs"]
    elif step_to_do == "pmtau":
        return ["cortical_thick"]
    elif step_to_do == "t1_pet_suvr":
        # print("parent_steps are t1_pet_reg and inf_cereb_mask")
        ##inf_cereb_mask implies wbseg already done
        ## amy doesn't use inf_cereb_mask ... 
        return ["t1_pet_reg", "inf_cereb_mask"]
    elif step_to_do == "pet_reg_qc":
        return ["t1_pet_reg"]
    elif step_to_do == "flair_skull_strip": 
        return []
    else:
        # print("step is stats, use *date_id as wait code ")
        return []
