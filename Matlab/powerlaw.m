function [p_in, p_out, P_in, P_out, PL_in_rv,PL_out_rv] =...
    powerlaw(k,k_min,k_max,A_cal,ncalibs,nsims)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% Generating a truncated power-law distribution
%%% Input variables are the control parameter set
%%% Sample from power-law distribution and use Monte Carlo simulation
%%% and averaging to obtain the degree-sequence to be passed to the 
%%% bidirectional Havel-Hakimi Algorithm

%%% By Nicolas K. Scholtes, April 2014

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% STEP 1: Defining the power law
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Truncated power-law pdf

p_in = zeros(ncalibs, numel(k));
p_out = p_in;

k_diff_in = zeros(1,ncalibs);
k_diff_out = k_diff_in;

mom = [1 2 3 4];

mu_in = zeros(1,ncalibs);
mu_out = mu_in;

var_in = zeros(1,ncalibs);
var_out = var_in;

for i=1:ncalibs
    
   for j = 1:numel(k)
       
   k_diff_in(i) = k_max.^(1-A_cal(i,1))-k_min.^(1-A_cal(i,1));
   k_diff_out(i) =  k_max.^(1-A_cal(i,2))-k_min.^(1-A_cal(i,2));

    
    % PDF
    p_in(i,j) = ((1-A_cal(i,1))*k(j).^(-A_cal(i,1)))/(k_diff_in(i));
    p_out(i,j) = ((1-A_cal(i,2))*k(j).^(-A_cal(i,2)))/(k_diff_out(i));
    
    %CDF
    P_in(i,j) = (k(j).^(1-A_cal(i,1))-k_min.^(1-A_cal(i,1)))/(k_diff_in(i));
    P_out(i,j) = (k(j).^(1-A_cal(i,1))-k_min.^(1-A_cal(i,2)))/(k_diff_out(i));

   end
   
%Intersection of two curves as a function of control parameters
   
k_int(i) = (((1-A_cal(i,1))*(k_diff_out(i)))/((1-A_cal(i,2))*...
    (k_diff_in(i)))).^(1/(A_cal(i,1)-A_cal(i,2)));

pk_int(i) = (((1-A_cal(i,2))/(k_diff_out(i))).^(A_cal(i,1))...
    *((k_diff_in(i))/(1-A_cal(i,1)))...
    .^(A_cal(i,2))).^(1/(A_cal(i,1)-A_cal(i,2)));

%Theoretical nth moments

%Mean

mu_in(i) = ((1-A_cal(i,1))/((mom(1)+1)-A_cal(i,1)))*...
    ((k_max^((mom(1)+1)-A_cal(i,1))-k_min^((mom(1)+1)-A_cal(i,1)))...
    /k_diff_in(i));

mu_out(i) = ((1-A_cal(i,2))/((mom(1)+1)-A_cal(i,2)))*...
    ((k_max^((mom(1)+1)-A_cal(i,2))-k_min^((mom(1)+1)-A_cal(i,2)))...
    /k_diff_out(i));

%Variance

var_in(i) = ((1-A_cal(i,1))/((mom(2)+1)-A_cal(i,1)))*...
    ((k_max^((mom(2)+1)-A_cal(i,1))-k_min^((mom(2)+1)-A_cal(i,1)))...
    /k_diff_in(i));

var_out(i) = ((1-A_cal(i,2))/((mom(2)+1)-A_cal(i,2)))*...
    ((k_max^((mom(2)+1)-A_cal(i,2))-k_min^((mom(2)+1)-A_cal(i,2)))...
    /k_diff_out(i));

end

disp('######################################################################')

disp('The population means of the in-degree distributions are')
disp(mu_in)

disp('The population means of the out-degree distributions are')
disp(mu_out)

disp('The population variances of the in-degree distributions are')
disp(var_in)

disp('The population variances of the out-degree distributions are')
disp(var_out)


%%% Check that the CDF is well-behaved (integral over range = 1)

threshold = 1e-10;
syms u

disp('######################################################################')

disp('-------Check that the CDF is well-behaved-------')

for i = 1:ncalibs

pdf_in = ((1-A_cal(i,1))*u.^(-A_cal(i,1)))/(k_diff_in(i));
pdf_out = ((1-A_cal(i,2))*u.^(-A_cal(i,2)))/(k_diff_out(i));

CDF_in_range = simplify(int(pdf_in,k_min,k_max));
CDF_out_range = simplify(int(pdf_out,k_min,k_max));



if (CDF_in_range<=1-threshold || CDF_in_range<1+threshold &&...
        CDF_out_range<=1-threshold || CDF_out_range<=1+threshold)
    disp('Well-behaved CDF')
else
    disp('Not a well-behaved CDF')
end

end

clearvars u

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% STEP 2: Random variate generation from power law
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% Using inverse transform sampling: generate quantiles using random draws
%%% from the uniform distribution

PL_in_rv = zeros(ncalibs,nsims);
PL_out_rv = PL_in_rv;

em_mean_in = zeros(1,ncalibs);
em_mean_out = em_mean_in;
em_var_in = zeros(1,ncalibs);
em_var_out = em_var_in;

for i=1:ncalibs
    for j=1:nsims

        u = rand(1,2);

        PL_in_rv(i,j) = (u(1)*(k_diff_in(i))+k_min.^(1-A_cal(i,1))).^(1/(1-A_cal(i,1)));
        PL_out_rv(i,j) = (u(2)*(k_diff_out(i))+k_min.^(1-A_cal(i,2))).^(1/(1-A_cal(i,2)));

    end
    
%Empirical moments

em_mean_in(i) = mean(PL_in_rv(i,:));
em_mean_out(i) = mean(PL_out_rv(i,:));

em_var_in(i) = var(PL_in_rv(i,:));
em_var_out(i) = var(PL_out_rv(i,:));

end

disp('######################################################################')

disp('The empirical means of the in-degree distributions are')
disp(em_mean_in)

disp('The empirical means of the out-degree distributions are')
disp(em_mean_out)

disp('The empirical variances of the in-degree distributions are')
disp(em_var_in)

disp('The empirical variances of the out-degree distributions are')
disp(em_var_out)


end

