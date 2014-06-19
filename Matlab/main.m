function [] = main()

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% Top-level function
%%% Contains the control parameter set which are passed to subfunctions
%%% as arguments
%%% Calls sub-functions in the following order:
%%%%%%1. Power law + Erdos-Gallai condition to obtain degree sequence
%%%%%%2. Pass realizable degree sequence to Havel-Hakimi algorithm
%%%%%%3. Combine node data with degrees to form the network
%%%%%%4. Contagion analysis on simulated network

%%% By Nicolas K. Scholtes, April 2014

clear all; close all; clc;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

tic

a_min = 2;
a_max = 3;
a_incr = 10;

a = linspace(a_min,a_max,a_incr);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% alpha-calibrations
%%% Convention, 1st el = in-par, 2nd el = out-par
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ncalibs = 4;
A_cal = zeros(ncalibs,2);
    
%%%1. a_in > a_out (large margin)

A_cal(1,:) = [a(9) a(2)];

%%%2. a_in > a_out (small margin)

A_cal(2,:) = [a(6) a(4)];

%%%3. a_out > a_in (large margin)

%N.B Below to ensure existence of moments

A_cal(3,:) = [a(1)+0.01 a(10)-0.01];

%%%4. a_out > a_in (small margin)

A_cal(4,:) = [a(3) a(7)];

k_min = 1;
k_max = 50;
k_incr = 1000;

k = linspace(k_min,k_max,k_incr);

numel(a);
numel(k);

nsims = 100000;

[p_in,p_out,P_in,P_out, PL_in_rv,PL_out_rv] = ...
    powerlaw(k,k_min,k_max,A_cal,ncalibs,nsims);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Creating the degree-sequence: two alternative methods
%%% 1. Random subsampling from empirical distribution
%%% 2. Rolling window + within-window mean of ordered vector
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

nbanks = 1000;

V_in_1 = zeros(ncalibs,nbanks);
V_out_1 = V_in_1;

el_choice_in = zeros(1,nbanks);
el_choice_out = el_choice_in;

V_in_2 = zeros(ncalibs,nbanks);
V_out_2 = V_in_2;


for i = 1:ncalibs
    for j=1:nbanks
        
        %1. Draws from uniform determine which element to choose
    
        el_choice_in(j) = round(rand*nsims);
        el_choice_out(j) =round(rand*nsims);
        
        V_in_1(i,j) = round(PL_in_rv(i,el_choice_in(j)));
        V_out_1(i,j) = round(PL_out_rv(i,el_choice_out(j)));
        
        %2. Window size = 1000 moving across 10,000 elements to create a 
        %   100-element vector (unordered degree sequence)
        
        RW_LB = nbanks*(j-1)+1;
        RW_UB = nbanks*j;
        
        V_in_2(i,j) = round(mean(PL_in_rv(i,RW_LB:RW_UB)));
        V_out_2(i,j) = round(mean(PL_out_rv(i,RW_LB:RW_UB)));

        
    end
end

%Finalizing the degree sequence to be passed to EG condition

in_degseq_1 = sort(V_in_1,2,'descend');
out_degseq_1 = sort(V_out_1,2,'descend');
in_degseq_2 = sort(V_in_2,2,'descend');
out_degseq_2 = sort(V_out_2,2,'descend');

disp('######################################################################')


disp('---Computing the sums of the degree sequences for each calibration---')


disp('The in-degree sequence sum using method 1 is:')
%disp(in_degseq_1)
disp(sum(in_degseq_1,2))


disp('The out-degree sequence sum using method 1 is:')
%disp(out_degseq_1)
disp(sum(out_degseq_1,2))


disp('The in-degree sequence sum using method 2 is:')
%disp(in_degseq_2)
disp(sum(in_degseq_2,2))


disp('The out-degree sequence sum using method 2 is:')
%disp(out_degseq_2)
disp(sum(out_degseq_2,2))





plots(k, p_in,p_out,P_in,P_out,PL_in_rv, PL_out_rv);

toc

end