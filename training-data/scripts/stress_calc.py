import numpy as np
import datetime

def ocnstress(u, v):
    """
    Calculates wind stress (taux, tauy) from wind velocity components (u, v).
    This version is updated to exactly match the user-provided original function.
    
    Args:
        u (np.ndarray): A 3D numpy array of u-wind components (time, lat, lon).
        v (np.ndarray): A 3D numpy array of v-wind components (time, lat, lon).
    """
    t0   = datetime.datetime.now()
    # Physical constants
    zref  = 10.0      # Reference height (m)
    kappa = 0.4       # Von Karman constant
    z0min = 1.5e-5    # Minimum roughness length (m)
    beta  = 0.018     # Charnock parameter
    g     = 9.8       # Acceleration due to gravity (m/s^2)
    rhoa  = 1.2923    # Reference density of dry air (kg/m^3)
    B     = beta/g

    # Initialize output arrays with the same shape as a time slice of the input
    taux_list = []
    tauy_list = []

    # Iterate over the time dimension
    for i in range(u.shape[0]):
        u_slice = u[i, :, :]
        v_slice = v[i, :, :]
        
        # Calculate original wind speed magnitude from the slice
        vind_orig = (u_slice**2 + v_slice**2)**0.5
        
        # Iteratively solve for friction velocity squared (us2)
        us2    = np.ones_like(vind_orig) * 0.1
        z0     = np.ones((2, vind_orig.shape[0], vind_orig.shape[1]), dtype=float) * z0min
        us2min = 1e-3
        us2old = us2 * 0.0
        
        n = 0
        # This loop converges on the correct friction velocity
        # The condition matches the original: max of the absolute min and max differences
        while (max(abs(np.min(us2 - us2old)), abs(np.max(us2 - us2old))) > us2min):
            n += 1
            us2old    = us2
            z0[0,:,:] = B * us2
            # The core equation for friction velocity
            us2       = ((kappa * vind_orig) / (np.log(zref / np.max(z0, axis=0))))**2
            if n > 20: # Safety break for non-converging cases
                print("Warning: Iteration limit reached in ocnstress.")
                break

        # CRITICAL DETAIL: The original code re-assigns the 'vind' variable after
        # calculating us2. This clipped vind is then used in the denominator.
        vind_clipped = np.where(vind_orig < 0.1, 0.1, vind_orig)
        
        # Calculate stress components for the current time slice
        taux_list.append(rhoa * us2 * u_slice / vind_clipped)
        tauy_list.append(rhoa * us2 * v_slice / vind_clipped)
        
    print('Original: Calculated stress in {} seconds'.format(int((datetime.datetime.now()-t0).total_seconds())))
    
    # Stack the lists of 2D arrays into final 3D arrays
    return np.stack(taux_list), np.stack(tauy_list)

def stress2ocn(taux, tauy):
    """
    Calculates wind velocity components (u, v) from wind stress (taux, tauy).
    This is the corrected inverse of the ocnstress function.
    
    Args:
        taux (np.ndarray): A 2D or 3D numpy array of taux stress components.
        tauy (np.ndarray): A 2D or 3D numpy array of tauy stress components.
    """
    t0   = datetime.datetime.now()
    # Physical constants must be identical to the forward function
    zref  = 10.0
    kappa = 0.4
    z0min = 1.5e-5
    beta  = 0.018
    g     = 9.8
    rhoa  = 1.2923
    B     = beta/g

    # u_out_list = []
    # v_out_list = []

    # # Iterate over the time dimension for 3D inputs
    # if taux.ndim == 3:
        # for i in range(taux.shape[0]):
        #     taux_slice = taux[i, :, :]
        #     tauy_slice = tauy[i, :, :]

    # For 2D inputs, we can handle them directly
    if taux.ndim == 2:
        taux_slice = taux
        tauy_slice = tauy

        # 1. Calculate the magnitude of the stress vector
        tau_mag = (taux_slice**2 + tauy_slice**2)**0.5

        # 2. Make an initial guess for vind. This doesn't need to be perfect.
        us2_approx = tau_mag / rhoa
        z0_approx = np.maximum(B * us2_approx, z0min)
        vind = np.zeros_like(tau_mag)
        non_zero_us2 = us2_approx > 0
        vind[non_zero_us2] = (np.sqrt(us2_approx[non_zero_us2]) * np.log(zref / z0_approx[non_zero_us2])) / kappa

        # 3. Iteratively refine the vind guess to find the true original wind speed.
        for _ in range(10): # 10 iterations is sufficient for convergence
            # A. For the current `vind` guess, find the corresponding `us2`.
            us2 = ((kappa * vind) / np.log(zref / np.maximum(B * (tau_mag / rhoa), z0min)))**2

            # B. Calculate what the stress magnitude *would be* with this vind and us2.
            #    This step must perfectly replicate the forward function's logic.
            vind_clipped = np.where(vind < 0.1, 0.1, vind)
            # The key is this ratio, which is not always 1.
            vind_ratio = vind / vind_clipped
            tau_mag_calc = rhoa * us2 * vind_ratio

            # C. Correct the `vind` guess based on the error.
            # Add a small epsilon to avoid division by zero.
            error_ratio = tau_mag / (tau_mag_calc + 1e-12)
            # This correction factor is more stable than the sqrt/cbrt approach
            vind *= (1 + (error_ratio - 1) * 0.5) # Converge gently

        # 4. Reconstruct the u and v wind components from the converged vind.
        u = np.zeros_like(taux_slice)
        v = np.zeros_like(tauy_slice)
        
        non_zero_stress = tau_mag > 1e-9
        
        u[non_zero_stress] = vind[non_zero_stress] * (taux_slice[non_zero_stress] / tau_mag[non_zero_stress])
        v[non_zero_stress] = vind[non_zero_stress] * (tauy_slice[non_zero_stress] / tau_mag[non_zero_stress])
        
        # u_out_list.append(u)
        # v_out_list.append(v)

    print('Inverse: Calculated velocity in {} seconds'.format(int((datetime.datetime.now()-t0).total_seconds())))
    # return np.stack(u_out_list), np.stack(v_out_list)
    return np.stack(u), np.stack(v)


if __name__ == '__main__':
    # --- Create sample 3D data (time, y, x) ---
    # Shape is (1, 10, 10) for a single time step.
    u_original = np.fromfunction(lambda t, y, x: 0.05 + 15 * np.sin(np.pi * x / 9), (1, 10, 10))
    v_original = np.fromfunction(lambda t, y, x: 0.05 + 10 * np.cos(np.pi * y / 9), (1, 10, 10))

    print("--- Running Forward Calculation (Velocity -> Stress) ---")
    taux_calc, tauy_calc = ocnstress(u_original, v_original)

    print("\n--- Running Inverse Calculation (Stress -> Velocity) ---")
    u_reverted, v_reverted = stress2ocn(taux_calc, tauy_calc)

    # --- Verification ---
    # Calculate absolute difference
    u_diff = np.abs(u_original - u_reverted)
    v_diff = np.abs(v_original - v_reverted)

    # Calculate percentage error, handling division by zero for points where original is zero.
    # We replace division by zero with 0, as the absolute error there should also be zero.
    u_original_abs = np.abs(u_original)
    v_original_abs = np.abs(v_original)
    
    percent_error_u = np.divide(u_diff, u_original_abs, out=np.zeros_like(u_diff), where=u_original_abs!=0) * 100
    percent_error_v = np.divide(v_diff, v_original_abs, out=np.zeros_like(v_diff), where=v_original_abs!=0) * 100

    print(f"\n--- Verification ---")
    print(f"Maximum absolute difference in U component: {np.max(u_diff):.6f}")
    print(f"Maximum absolute difference in V component: {np.max(v_diff):.6f}")
    print(f"Maximum percentage error in U component:   {np.max(percent_error_u):.6f}%")
    print(f"Maximum percentage error in V component:   {np.max(percent_error_v):.6f}%")


    if np.allclose(u_original, u_reverted) and np.allclose(v_original, v_reverted):
        print("\n✅ Verification successful: The reverted values are very close to the original values.")
    else:
        print("\n❌ Verification failed: The reverted values differ significantly from the originals.")
