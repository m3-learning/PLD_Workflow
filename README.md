# Utility functions for Pulsed Laser Deposition

## pld_functions.py: 

  Include digital form for growth condition recording and plume imaging management.

  Usage: 

  1. For condition recording only: 
    
    if __name__ == "__main__":
      app = QApplication(sys.argv)
      window = PLD_Form(version="parameter")
      window.show()
      app.exec_()

  2. With plume recording and management: 
  
    if __name__ == "__main__":
      app = QApplication(sys.argv)
      window = PLD_Form(version="plume")
      window.show()
      app.exec_()
         
## metrics_functions.py: 

  Used to plot metrics of plumes for plume dynamic analysis.
  
  Usage: 
  
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
