#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rpt_dosi.images as rim
import rpt_dosi.utils as he
from rpt_dosi.utils import warning
import math
import shutil

if __name__ == "__main__":
    # folders
    data_folder, ref_folder, output_folder = he.get_tests_folders("test001d")
    print(f"Input data folder = {data_folder}")
    print(f"Ref data folder = {ref_folder}")
    print(f"Output data folder = {output_folder}")
    print()

    # test scale activity
    warning(f'set metadata Bq, SPECT and scaling')
    spect_input = data_folder / "spect_8.321mm.nii.gz"
    spect_output = output_folder / "spect_activity.nii.gz"
    shutil.copy(spect_input, spect_output)
    spect = rim.read_spect(spect_output, "Bq")
    print(f'total activity', spect.compute_total_activity())
    t1 = spect.compute_total_activity()
    s = spect.voxel_volume_cc / 0.666
    cmd = f"rpt_spect_update -i {spect_input} -o {spect_output} -s {s} -u Bq"
    cmd_ok = he.run_cmd(cmd, data_folder / "..")
    sp = rim.read_spect(spect_output)
    t2 = sp.compute_total_activity()
    print(f'total activity', sp.compute_total_activity())
    spect_ref = ref_folder / "spect_activity_ref.nii.gz"
    b = rim.test_compare_images(spect_output, spect_ref, tol=1e-6)
    he.print_tests(b, f"SPECT calibration activity {spect_output}  vs  {spect_ref}")
    is_ok = b and cmd_ok

    # test convert Bq to Bqml
    print()
    warning(f'convert Bq to Bqml')
    cmd = f"rpt_spect_update -i {spect_output} -o {spect_output} --convert Bq/mL"
    cmd_ok = he.run_cmd(cmd, data_folder / "..")
    sp = rim.read_spect(spect_output)
    ok = math.isclose(t2, sp.compute_total_activity(), rel_tol=1e-6) and cmd_ok
    he.print_tests(ok, f'Compare total activity {t2} and {sp.compute_total_activity()} ? {ok}')
    is_ok = is_ok and ok

    # convert back as Bq (same activity)
    print()
    warning(f'convert back to Bq')
    sp.convert_to_bq()
    ok = math.isclose(t2, sp.compute_total_activity(), rel_tol=1e-6)
    he.print_tests(ok, f'Compare total activity {t2} and {sp.compute_total_activity()}')
    is_ok = is_ok and ok

    # SUV
    print()
    warning(f'SUV')
    cmd = f"rpt_image_set_metadata -i {spect_output} --tag injection_activity_mbq 7400 --tag body_weight_kg 80"
    cmd_ok = he.run_cmd(cmd, data_folder / "..")
    sp = rim.read_spect(spect_output)
    sp.convert_to_suv()
    sp.write(spect_output)
    ok = math.isclose(t2, sp.compute_total_activity(), rel_tol=1e-6)
    he.print_tests(ok, f'Compare total activity {t2} and {sp.compute_total_activity()}')
    is_ok = is_ok and ok

    # end
    he.test_ok(is_ok)
