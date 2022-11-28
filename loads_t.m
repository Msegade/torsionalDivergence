function loads

args = argv();
init = str2num(args{1});

if init == 1
    wing_Rx={{RY}};
    disp('init')
elseif init == 0
    mdict=load('RY.mat');
    wing_Rx = {{RY}} + mdict.RY;
    disp('no init')
end

[load_Uy,load_Uz,load_Um] = loads_iteration(wing_Rx);

end

function [load_Uy,load_Uz,load_Um] = loads_iteration(wing_Rx)

    load('coefficients_filtered.mat');
    
    %U_DT=1012.9;
    %U_DT=850;
    U_DT={{U}};
    %U_DT = 1;
    B = [3.7, 3.4, 3.1, 2.8, 2.5, 2.2, 1.9, 1.6, 1.3, 1.0];
    nu_dyn_visc=1.5e-5;
    rho_air=1.22; % T
    Re_val=rho_air*U_DT*B/nu_dyn_visc;

    Re_val(Re_val > 2e7) = 2e7;

    cd = interp2(angles_data, reynolds_data, Cd_data', wing_Rx, Re_val, 'linear');
    cl = interp2(angles_data, reynolds_data, Cl_data', wing_Rx, Re_val, 'linear');
    cm = interp2(angles_data, reynolds_data, Cm_data', wing_Rx, Re_val, 'linear');

    %surf(angles_data, reynolds_data, Cd_data')
   
    l_elemento = [1.35, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.45];
    load_Uy=0.5* rho_air * (U_DT^2) * B       .* cd .* l_elemento;
    load_Uz=0.5* rho_air * (U_DT^2) * B       .* cl .* l_elemento;
    load_Um=0.5* rho_air * (U_DT^2) * (B.^2)  .* cm .* l_elemento;

    save('load_Uy.mat', 'load_Uy')
    save('load_Uz.mat', 'load_Uz')
    save('load_Um.mat', 'load_Um')
    
    
end
