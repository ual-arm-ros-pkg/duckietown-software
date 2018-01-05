import shutil

import duckietown_utils as dtu
from easy_regression.conditions.interface import RTCheck
from duckietown_utils.unit_tests import get_output_dir_for_test


def run(which, expect):
    v = False
    cwd = get_output_dir_for_test()
#     cwd = dtu.create_tmpdir('run-regression')
    try:
        cmd = ['rosrun', 'easy_regression', 'run', 
               '--expect', expect, 
               '--test', which,
               '-c', 'rmake']
        dtu.system_cmd_result(cwd, cmd,
              display_stdout=v,
              display_stderr=v,
              raise_on_error=True)
    finally:
        shutil.rmtree(cwd)  
    
@dtu.unit_test
def run_abnormal1():
    run('expect_abnormal1', RTCheck.ABNORMAL)


@dtu.unit_test
def run_abnormal3():
    run('expect_abnormal3', RTCheck.ABNORMAL)
    
    
@dtu.unit_test
def run_dontrun1():
    try:
        run('expect_dontrun1', RTCheck.OK)
    except dtu.CmdException as e:
        if 'NOT-existing' in e.res.stderr:
            return
        raise
    
    
@dtu.unit_test
def run_ok1():
    run('expect_ok1', RTCheck.OK)

@dtu.unit_test
def run_nodata1():
    run('expect_nodata1', RTCheck.NODATA)
    
@dtu.unit_test
def run_nodata2():
    run('expect_nodata2', RTCheck.NODATA)

@dtu.unit_test
def run_fail1():
    run('expect_fail1', RTCheck.FAIL)
    

@dtu.unit_test
def run_rt_small_video():
    run('rt_small_video', RTCheck.OK)
    
    
    
if __name__ == '__main__':
    dtu.run_tests_for_this_module()
    
    