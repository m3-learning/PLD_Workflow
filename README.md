# Instruction to open PLD digital form:

## 1. Start the program:
  1). Click "Start" - "Anaconda Prompt"
  2). Copy the following code in the opened terminal:
     
     conda activate pld
     
     cd C:/Image/PLD_Workflow/
  
## 2. For parameter recording only: 

1). Start the form by copying the following code in the terminal:

      python examples/pld_app_parameter.py
      
2). Fill in growth conditions and customized information

3). After finishing all recording and converting all videos, click "Save Parameters", and "Save to HDF5 and Upload". It may take a longer time to finish. Local HDF5 file (plume images) and JSON file (condition) will be saved locally and uploaded to the cloud.
     
     
## 3. For parameter and plume recording: 
  
1). Start the form by copying the following code in the opened terminal:

      python  examples/pld_app_plume.py
      
2). Fill in growth conditions and customized information

3). For every ablation cycle (different targets with pre-ablation and ablation):

  1>. Click the button "Move Videos to Pre-ablation Folder" or "Move Videos to Ablation Folder."

  2>. Use "HPV-X Viewer" software on the desktop to convert the raw file to readable images: 
"File" -> "Convert" -> Find the directory labelled start with your growth id -> Select all and click "CONVERT" 


## 4. Addition instruction for camera position calibration:

1). Open Software "HPV-X" on desktop

2). Click the "Live" button and increase "EXPOSE" to 10,000,000ns to align the camera focus between the target and substrate holder.

3). Decrease the "EXPOSE" to 2,000,000ns and Click "REC" to start recording before ablation.

<!-- 
# PLDForm README:
## Utility functions for Pulsed Laser Deposition

### PLDForm.py: 

  Include a digital form for growth condition recording and plume imaging management.

  Usage: 

  1. For condition recording only: 
    
    if __name__ == "__main__":
      app = QApplication(sys.argv)
      window = GenerateForm(version="parameter")
      window.show()
      app.exec_()

  2. With plume recording and management: 
  
    if __name__ == "__main__":
      app = QApplication(sys.argv)
      window = GenerateForm(version="plume")
      window.show()
      app.exec_()
      


  3>. Waiting time depends on how many videos are selected.

4). After finishing all recording and converting all videos, click "Save Parameters", and "Save to HDF5 and Upload". It may take a longer time to finish.
 -->



<!-- # PlumeEvaluation README:

Used to plot metrics of plumes for dynamic plume analysis.

Usage in python: 
  
  0. Import functions:

    from metrics_functions import show_h5_dataset_name
    from metrics_functions import load_h5_examples
    from metrics_functions import show_images
    from metrics_functions import plumes_to_df
    from metrics_functions import plot_metrics
    from metrics_functions import process_func
    import numpy as np

  1. Load and visualize plume examples: 
  
    ds_path = '/root_dir/pld_plumes/h5_dataset_name.h5'
    class_name = 'PLD_Plumes'
    ds_name = '0-SrRuO3'
    show_h5_dataset_name(ds_path, class_name)
    plumes = load_h5_examples(ds_path, class_name, ds_name, process_func, show=False)
    show_images(np.mean(plumes, axis=0), img_per_row=10)

  2. Convert to pandas DataFrame: 

    condition = 'experimental_condition'
    df = plumes_to_df(ds_path, ds_name, condition)
    df.sample(n=5)

  3. Plot the metrics based on condition or growth_index: 
  
    metrics_name = ['area', 'area_filled', 'axis_major_length', 
                'axis_minor_length', 'centroid-1', 'centroid-2', 'orientation', 
                'eccentricity', 'perimeter', 'velocity'] 
    plot_metrics(df, metrics_name, label_with='condition')
    plot_metrics(df, metrics_name, label_with='growth_index')  
 -->
