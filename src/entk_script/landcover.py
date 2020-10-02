"""
Author: Ioannis Paraskevakos
License: MIT
Copyright: 2018-2019
"""

import os
import csv
import radical.entk as re

from .executor import Executor
from ..discovery import Discovery


class Seals(Executor):
    '''
    :Class Seals:
    This class instantiates the Seals use case.
    :Additional Parameters:
        :input_path: The path to the input images
        :ouptut_path: Path to the output images
        :scale_bands: The size of the scale bands
        :model: The model
        :model_path: Path of a custom model
        :hyperparameters: Hyperparameter Set
    '''
    # pylint: disable=too-many-arguments
    def __init__(self, name, resources, project=None, input_path=None):

        super(Seals, self).__init__(name=name,
                                    resource=resources['resource'],
                                    queue=resources['queue'],
                                    walltime=resources['walltime'],
                                    cpus=resources['cpus'],
                                    project=project)
        self._data_input_path = input_path
        self._req_modules = None
        self._pre_execs = None
        self._env_var = os.environ.get('VE_SEALS')
        if self._res_dict['resource'] == 'xsede.bridges':

            self._req_modules = ['python3']

            self._pre_execs = ['source %s' % self._env_var
                               + '/bin/activate',
                               'export PYTHONPATH=%s/' % self._env_var
                               + 'lib/python3.5/site-packages']

        self._logger.info('LandCover initialized')
    # pylint: disable=too-many-arguments

    def run(self):
        '''
        This is a blocking execution method. This method should be called to
        execute the usecase.
        '''
        try:
            self._logger.debug('Running workflow')
            self._run_workflow()
        finally:
            self._terminate()

    def _resolve_pre_execs(self):
        '''
        This is a utils method. It takes the list of modules and return a list
        of pre_exec commands
        '''

        tmp_pre_execs = list()
        for module in self._req_modules:
            tmp_pre_exec = 'module load %s' % module
            self._logger.debug("Preexec added: %s", tmp_pre_exec)
            tmp_pre_execs.append(tmp_pre_exec)

        tmp_pre_execs = tmp_pre_execs + self._pre_execs

        return tmp_pre_execs

    # pylint: disable=unused-argument
    def _generate_pipeline(self, name, pre_execs, image, image_size):

        '''
        This function creates a pipeline for an image that will be analyzed.

        :Arguments:
            :name: Pipeline name, str
            :image: image path, str
            :image_size: image size in MBs, int
            :tile_size: The size of each tile, int
            :model_path: Path to the model file, str
            :model_arch: Prediction Model Architecture, str
            :model_name: Prediction Model Name, str
            :hyperparam_set: Which hyperparameter set to use, str
        '''
        # Create a Pipeline object
        entk_pipeline = re.Pipeline()
        entk_pipeline.name = name
        # Preprocessing raw to radiance
        stage0 = re.Stage()
        stage0.name = '%s-S0' % (name)
        # Create Task 1, raw to radiance
        task0 = re.Task()
        task0.name = '%s-T0' % stage0.name
        task0.pre_exec = pre_execs
        task0.executable = 'rad.py'  # Assign tak executable
        # Assign arguments for the task executable
        task0.arguments = ['--input_image=%s' % image.split('/')[-1],
                           # This line points to the local filesystem of the
                           # node that the tiling of the image happened.
                           '--output_folder=%s' % task0.name]
        task0.link_input_data = [image]
        task0.cpu_reqs = {'processes': 1, 'threads_per_process': 4,
                          'process_type': None, 'thread_type': 'OpenMP'}
        # task0.lfs_per_process = image_size

        stage0.add_tasks(task0)
        # Add Stage to the Pipeline
        entk_pipeline.add_stages(stage0)

        # Option 1 atm_corr.py might need to skip 
        stage1 = re.Stage()
        stage1.name = '%s-S1' % (name)
        # Create Task 1, training
        task1 = re.Task()
        task1.name = '%s-T1' % stage1.name
        task1.pre_exec = pre_execs
        task1.executable = 'atmcorr_specmath.py'  # Assign task executable
        # Assign arguments for the task executable
        task1.arguments = ['--input_image', image.split('/')[-1],
                           (entk_pipeline.name, stage0.name,
                            task0.name, task0.name),
                           '--output_folder', './%s' % image.split('/')[-1].
                           split('.')[0]]
        #task1.link_input_data = ['$SHARED/%s' % self._model_name]
        task1.cpu_reqs = {'processes': 1, 'threads_per_process': 1,
                          'process_type': None, 'thread_type': 'OpenMP'}
        # Download resuting images
        # task1.tag = task0.name

        stage1.add_tasks(task1)
        # Add Stage to the Pipeline
        entk_pipeline.add_stages(stage1)

        # Radiance to reflectance
        stage2 = re.Stage()
        stage2.name = '%s-S1' % (name)
        # Create Task 1, training
        task2 = re.Task()
        task2.name = '%s-T1' % stage1.name
        task2.pre_exec = pre_execs
        task2.executable = 'refl.py'  # Assign task executable
        # Assign arguments for the task executable
        task2.arguments = ['--input_image', image.split('/')[-1],
                           (entk_pipeline.name, stage0.name,
                            task0.name, task0.name),
                           '--output_file', './%s' % image.split('/')[-1].
                           split('.')[0]]
        #task1.link_input_data = ['$SHARED/%s' % self._model_name]
        task2.cpu_reqs = {'processes': 1, 'threads_per_process': 1,
                          'process_type': None, 'thread_type': 'OpenMP'}
        # Download resuting images
        task2.download_output_data = ['%s/ > %s' % (image.split('/')[-1].
                                                    split('.')[0],
                                                    image.split('/')[-1])]
        # task1.tag = task0.name

        stage2.add_tasks(task2)
        # Add Stage to the Pipeline
        entk_pipeline.add_stages(stage2)

        # Simple Classification
        stage3 = re.Stage()
        stage3.name = '%s-S1' % (name)
        # Create Task 1, training
        task3 = re.Task()
        task3.name = '%s-T1' % stage1.name
        task3.pre_exec = pre_execs
        task3.executable = 'class.py'  # Assign task executable
        # Assign arguments for the task executable
        task3.arguments = ['--input_image', image.split('/')[-1],
                           (entk_pipeline.name, stage3.name,
                            task3.name, task3.name),
                           '--output_folder', './%s' % image.split('/')[-1].
                           split('.')[0]]
        #task1.link_input_data = ['$SHARED/%s' % self._model_name]
        task3.cpu_reqs = {'processes': 1, 'threads_per_process': 1,
                          'process_type': None, 'thread_type': 'OpenMP'}
        if shapefile:
            task3.post_exec = 'create a shape file and download'
        # task1.tag = task0.name

        stage3.add_tasks(task3)

        # TODO: Second Classification might need to be overriden based on user preference
        # otherwise executed 
        # if separate_features:
        #     # Add a masking stage
        #     stage4 = re.Stage()
        #     stage4.name = '%s-S1' % (name)
        #     # Seperate features with three tasks and add them to the same stage
        #     task4 = re.Task()
        #     task4.name = '%s-T1' % stage1.name
        #     task4.pre_exec = pre_execs
        #     task4.executable = 'class.py'  # Assign task executable
        #     # Assign arguments for the task executable
        #     task4.arguments = ['--input_image', image.split('/')[-1],
        #                        (entk_pipeline.name, stage3.name,
        #                         task3.name, task3.name),
        #                         'type'
        #                        '--output_folder', './%s' % image.split('/')[-1].
        #                        split('.')[0]]
        #     #task1.link_input_data = ['$SHARED/%s' % self._model_name]
        #     task4.cpu_reqs = {'processes': 1, 'threads_per_process': 1,
        #                       'process_type': None, 'thread_type': 'OpenMP'}
        #     if shapefile:
        #         task3.post_exec = 'create a shape file'
        #     # task1.tag = task0.name
        #
        #    stage3.add_tasks(task3)
        #    # Add Stage to the Pipeline
        #    entk_pipeline.add_stages(stage3)

        entk_pipeline.add_stages(stage5)

        return entk_pipeline

    # pylint: enable=unused-argument
    def _run_workflow(self):
        '''
        Private method that creates and executes the workflow of the use case.
        '''
        self._app_manager.shared_data = [os.path.abspath(self._model_path
                                                         + self._model_name)]
        self._logger.debug('Uploaded model %s',
                           os.path.abspath(self._model_path + self._model_name))
        discovery = Discovery(modules=self._req_modules,
                              paths=self._data_input_path,
                              pre_execs=self._pre_execs + ['module list',
                                                           'echo $PYTHONPATH',
                                                           'which python3'])
        discovery_pipeline = discovery.generate_discover_pipe()

        self._app_manager.workflow = set([discovery_pipeline])

        self._app_manager.run()
        images_csv = open('images0.csv')
        images = csv.reader(images_csv)
        _ = next(images)
        pre_execs = self._resolve_pre_execs()
        img_pipelines = list()
        idx = 0
        for [image, size] in images:
            img_pipe = self._generate_pipeline(name='P%s' % idx,
                                               pre_execs=pre_execs,
                                               image=image,
                                               image_size=int(size))
            img_pipelines.append(img_pipe)
            idx += 1

        self._app_manager.workflow = set(img_pipelines)

        self._app_manager.run()

    def _terminate(self):
        '''
        Stops the execution
        '''

        self._app_manager.resource_terminate()
