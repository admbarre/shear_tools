import os
import pandas as pd
import json
import re
import shutil

class ShearOffExp:
    def __init__(self,exp_dir):
        self.off_regex = r"LN(\d)_(\d)_MMStack_Pos(\d).ome.tif"
        self.exp_dir = exp_dir
        self.info_dir = f"{exp_dir}/info"
        self.info_path = f"{self.info_dir}/exp_info.json"

        self.images_dir = f"{exp_dir}/Images"
        self.grouped_dir = f"{exp_dir}/grouped"

        #self.get_exp_info()
    
    def init_exp(self):
        if os.path.exists(self.info_path):
            with open(self.info_path) as f:
                self.exp_info = json.load(f)
        else:
            self.cleanup_dir()

    def save_dict(self,save_path,save_dict):
        with open(save_path, "w") as f:
            json.dump(save_dict, f)

    # Runs if experiment has not been initialized (does not have info dir,
    # or files grouped)
    def cleanup_dir(self):
        os.mkdir(self.info_dir)

        all_files = []
        for root,dirs,files in os.walk(self.exp_dir):
            for f in files:
                all_files.append(f)
        
        # Initialize exp_info with sets to capture unique data
        exp_info = {
                "lanes" : set(),
                "flows" : set(),
                "positions": set(),
        }

        file_move_dict = {}
        for f in all_files:
            matches = re.search(self.off_regex,f)
            lane,flow,pos = matches.groups()

            # Generating associations between old file paths and where they 
            # will be moved
            old_path = f"{self.exp_dir}/LN{lane}_{flow}/{f}"
            new_path = f"{self.grouped_dir}/LN{lane}/pos{pos}/{f}"
            file_move_dict[old_path] = new_path

            exp_info["lanes"].add(lane)
            exp_info["flows"].add(flow)
            exp_info["positions"].add(pos)

        exp_info["lanes"] = sorted(list(exp_info["lanes"]))
        exp_info["flows"] = sorted(list(exp_info["flows"]))
        exp_info["positions"] = sorted(list(exp_info["positions"]))
        
        self.exp_info = exp_info
        self.save_dict(self.info_path,exp_info)

        self.file_move_dict = file_move_dict
        move_save_path = f"{self.info_dir}/grouped_move.json"
        self.save_dict(move_save_path,file_move_dict)

    def ungroup_files(self):
        pass

    # Probably want to make this not destructive...
    def group_files(self):
        os.mkdir(self.grouped_dir)
        old_dirs = set()
        for o,n in self.file_move_dict.items():
            os.makedirs(os.path.dirname(n),exist_ok=True)
            shutil.move(o,n)
            old_dir = os.path.dirname(o)
            old_dirs.add(old_dir)
        for o in list(old_dirs):
            os.rmdir(o)



if __name__ == "__main__":
    test_dir = "/Volumes/ADRIAN/confocal/05-12 TGI pGK L42 IQ nonbinder SHEAR"
    test_exp = ShearOffExp(test_dir)
    test_exp.init_exp()
    test_exp.group_files()


