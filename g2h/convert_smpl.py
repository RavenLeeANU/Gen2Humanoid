import numpy as np

def convert_to_smplx(hym_npz_path, output_path, frame_rate=30.0):
    
    data = np.load(hym_npz_path, allow_pickle=True)
    
    T = data['poses'].shape[0]
    hymotion_poses = data['poses']
    
    amass_poses = np.zeros((T, 165))
    
    amass_poses[:, :3] = hymotion_poses[:, :3]
    # amass_poses[:, :3] = data['Rh'] 
    
    amass_poses[:, 3:66] = hymotion_poses[:, 3:66]
    
    amass_poses[:, 66:156] = hymotion_poses[:, 66:156]
    
    # amass_poses[:, 156:165] = 0 
    
    amass_data = {}
    
    amass_data['poses'] = amass_poses.astype(np.float64)
    amass_data['trans'] = data['trans'].astype(np.float64)  
    amass_data['betas'] = data['betas'].squeeze().astype(np.float64) 
    
    amass_data['root_orient'] = amass_poses[:, :3].astype(np.float64) 

    amass_data['pose_body'] = amass_poses[:, 3:66].astype(np.float64)  
    amass_data['pose_hand'] = amass_poses[:, 66:156].astype(np.float64) 
    amass_data['pose_jaw'] = np.zeros((T, 3), dtype=np.float64) 
    amass_data['pose_eye'] = np.zeros((T, 6), dtype=np.float64)  
    
    amass_data['gender'] = data['gender'].item() if data['gender'].shape == (1,) else data['gender']
    amass_data['mocap_frame_rate'] = np.array([frame_rate], dtype=np.float64)
    amass_data['mocap_time_length'] = np.array([T / frame_rate], dtype=np.float64)
    amass_data['mocap_time_length'] = len(amass_data['betas'])
    np.savez(output_path, **amass_data)
    print(f"转换完成！已保存到: {output_path}")
    print(f"数据形状: poses={amass_poses.shape}, trans={amass_data['trans'].shape}")
    
    return amass_data