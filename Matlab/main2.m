function [] = main2()

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

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% alpha-calibrations
%%% Convention, 1st el = in-par, 2nd el = out-par
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ncalibs = 4;
A_cal = zeros(ncalibs,2);
eps1 = 0.05;
eps2 = 0.025;
eps3 = 0.075;
    
%%%1. a_in > a_out (large margin)

A_cal(1,:) = [a(9) a(2)];
%A_cal(1,:) = [a(6)+eps1 a(4)-eps3];


%%%2. a_in > a_out (small margin)

A_cal(2,:) = [a(6) a(4)];

%%%3. a_out > a_in (large margin)

%N.B Below to ensure existence of moments

A_cal(3,:) = [a(1)+0.01 a(10)-0.01];
%A_cal(3,:) = [a(6)+eps2 a(4)-eps1];


%%%4. a_out > a_in (small margin)

A_cal(4,:) = [a(3) a(7)];
%A_cal(4,:) = [a(6)-eps1 a(4)+eps3];


k_min = 1;
k_max = 50;
k_incr = 1000;

k = linspace(k_min,k_max,k_incr);

numel(a);
numel(k);

nsims = 100000;

[p_in,p_out,P_in,P_out, PL_in_rv,PL_out_rv] = ...
    powerlaw(k,k_min,k_max,A_cal,ncalibs,nsims);

size(PL_in_rv);
size(PL_out_rv);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Creating the degree-sequence by
%%% Random subsampling from empirical distribution
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

nbanks = 100;
nresample = 1000000;

V_in = zeros(ncalibs,nbanks,nresample);
V_out = V_in;

in_DS_c1pass = V_in;
out_DS_c1pass = in_DS_c1pass;

el_choice_in = zeros(1,nbanks);
el_choice_out = el_choice_in;

%So that the random 0 is not returned when drawing from the uniform

rand_LB = (nsims^(-1))/2;
rand_UB = 1;

sumtest = zeros(ncalibs,nresample);

for i = 1:ncalibs
    
    for k_1 = 1:nresample
        
        current_resample = [i, k_1]
    
        for j=1:nbanks
        
        %1. Draws from uniform determine which element to choose
        
        r = rand_LB + (rand_UB-rand_LB).*rand;
    
        el_choice_in(j) = round(r*nsims);
        el_choice_out(j) =round(r*nsims);
        
        V_in(i,j,k_1) = round(PL_in_rv(i,el_choice_in(j)));
        V_out(i,j,k_1) = round(PL_out_rv(i,el_choice_out(j)));
        
                   
        end
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Check that the degree-sequence is GRAPHICAL using the
%%% FR theorem which requires three N&S conditions:
%%% 1. SUM(in-degrees) = SUM(out-degrees)
%%% 2. #in-degrees, #out-degrees for all nodes must be not larger than the
%%%    number of other nodes it could connect to, or receive connection from
%%% 3. EG condition for BDS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  

%Condition 1

    if (sum(V_in(i,:,k_1)) == sum(V_out(i,:,k_1)))
        
        
        sumtest(i,k_1) = 1;
        in_DS_c1pass(i,:,k_1) = V_in(i,:,k_1);
        out_DS_c1pass(i,:,k_1) = V_out(i,:,k_1);
        
    else
        sumtest(i,k_1) = 0;
        in_DS_c1pass(i,:,k_1) = -1*ones(1,nbanks);
        out_DS_c1pass(i,:,k_1) = -1*ones(1,nbanks);
        
    end
        
    end

    %in_DS_c1pass(in_DS_c1pass==-1) = [];
    %out_DS_c1pass(out_DS_c1pass==-1) = [];
    
end

%%%Constructing the matrix of condition 1 passes for each calibration
    
    cal1_inDS_c1pass = in_DS_c1pass(1,:,:);
    cal2_inDS_c1pass = in_DS_c1pass(2,:,:);
    cal3_inDS_c1pass = in_DS_c1pass(3,:,:);
    cal4_inDS_c1pass = in_DS_c1pass(4,:,:);

    cal1_outDS_c1pass = out_DS_c1pass(1,:,:);
    cal2_outDS_c1pass = out_DS_c1pass(2,:,:);
    cal3_outDS_c1pass = out_DS_c1pass(3,:,:);
    cal4_outDS_c1pass = out_DS_c1pass(4,:,:);
    
    cal1_inDS_c1pass(cal1_inDS_c1pass==-1) = [];
    cal2_inDS_c1pass(cal2_inDS_c1pass==-1) = [];
    cal3_inDS_c1pass(cal3_inDS_c1pass==-1) = [];
    cal4_inDS_c1pass(cal4_inDS_c1pass==-1) = [];

    cal1_outDS_c1pass(cal1_outDS_c1pass==-1) = [];
    cal2_outDS_c1pass(cal2_outDS_c1pass==-1) = [];
    cal3_outDS_c1pass(cal3_outDS_c1pass==-1) = [];
    cal4_outDS_c1pass(cal4_outDS_c1pass==-1) = [];
    
    cal1_inDS_tot_pass = numel(cal1_inDS_c1pass)/nbanks;
    cal2_inDS_tot_pass = numel(cal2_inDS_c1pass)/nbanks;
    cal3_inDS_tot_pass = numel(cal3_inDS_c1pass)/nbanks;
    cal4_inDS_tot_pass = numel(cal4_inDS_c1pass)/nbanks;

    cal1_outDS_tot_pass = numel(cal1_outDS_c1pass)/nbanks;
    cal2_outDS_tot_pass = numel(cal2_outDS_c1pass)/nbanks;
    cal3_outDS_tot_pass = numel(cal3_outDS_c1pass)/nbanks;
    cal4_outDS_tot_pass = numel(cal4_outDS_c1pass)/nbanks;
 
    cal1_inDS_c1pass = vec2mat(cal1_inDS_c1pass,nbanks);
    cal2_inDS_c1pass = vec2mat(cal2_inDS_c1pass,nbanks);
    cal3_inDS_c1pass = vec2mat(cal3_inDS_c1pass,nbanks);
    cal4_inDS_c1pass = vec2mat(cal4_inDS_c1pass,nbanks);
    
    cal1_outDS_c1pass = vec2mat(cal1_outDS_c1pass,nbanks);
    cal2_outDS_c1pass = vec2mat(cal2_outDS_c1pass,nbanks);
    cal3_outDS_c1pass = vec2mat(cal3_outDS_c1pass,nbanks);
    cal4_outDS_c1pass = vec2mat(cal4_outDS_c1pass,nbanks);
        
       

% if (ismember(in_DS_c1pass(:,:,k),-1) && ...
%     ismember(out_DS_c1pass(:,:,k),-1))
%     
% [I,J] = ind2sub(size(in_DS_c1pass(:,:,k)),...
%     find(ismember(in_DS_c1pass(:,:,k),-1)));


    
%size(i)
%size(j)

%Finalizing the degree sequence to be passed to EG condition

%in_degseq_1 = sort(V_in,2,'descend');
%out_degseq_1 = sort(V_out,2,'descend');


disp('######################################################################')


disp('---Checking the sums of the passed degree sequences for each calibration---')

%Calibration 1

disp('++++++++++++++++++++++++++++CALIBRATION 1++++++++++++++++++++++++++++++')

if (cal1_inDS_tot_pass>0 && cal1_outDS_tot_pass > 0)
    
    disp('--------------------')
    
    disp('The number and fraction of condition 1 passes under CALIBRATION 1 is:')
    disp(cal1_inDS_tot_pass)
    disp(cal1_inDS_tot_pass/nresample)
    
    %disp('--------------------')    
    
%     disp('The sums of the passes are given by:')
%     
%     for i=1:cal1_inDS_tot_pass
%         
%     disp(sum(cal1_inDS_c1pass(i,:)))
%     %disp(sum(cal2_outDS_c1pass(i,:)))
%     
%     end
      
else
    disp('No degree-sequences pass condition 1')
end


%Calibration 2

disp('++++++++++++++++++++++++++++CALIBRATION 2++++++++++++++++++++++++++++++')

if (cal2_inDS_tot_pass>0 && cal2_outDS_tot_pass > 0)
    
    disp('--------------------')
    
    disp('The number and fraction of condition 1 passes under CALIBRATION 2 is:')
    disp(cal2_inDS_tot_pass)
    disp(cal2_inDS_tot_pass/nresample)
    
    disp('--------------------')    
    
    %disp('The sums of the passes are given by:')
    
%     for i=1:cal2_inDS_tot_pass
%         
%     disp(sum(cal2_inDS_c1pass(i,:)))
%     %disp(sum(cal2_outDS_c1pass(i,:)))
%     
%     end
      
else
    disp('No degree-sequences pass condition 1')
end

disp('++++++++++++++++++++++++++++CALIBRATION 3++++++++++++++++++++++++++++++')

if (cal3_inDS_tot_pass>0 && cal3_outDS_tot_pass > 0)
    
    disp('--------------------')
    
    disp('The number and fraction of condition 1 passes under CALIBRATION 3 is:')
    disp(cal3_inDS_tot_pass)
    disp(cal3_inDS_tot_pass/nresample)
    
    disp('--------------------')    
    
%     disp('The sums of the passes are given by:')
%     
%     for i=1:cal3_inDS_tot_pass
%         
%     disp(sum(cal3_inDS_c1pass(i,:)))
%     disp(sum(cal2_outDS_c1pass(i,:)))
%     
%     end
      
else
    disp('No degree-sequences pass condition 1')
end

disp('++++++++++++++++++++++++++++CALIBRATION 4++++++++++++++++++++++++++++++')

if (cal4_inDS_tot_pass>0 && cal4_outDS_tot_pass > 0)
    
    disp('--------------------')
    
    disp('The number and fraction of condition 1 passes under CALIBRATION 4 is:')
    disp(cal4_inDS_tot_pass)
    disp(cal4_inDS_tot_pass/nresample)
    
    disp('--------------------')    
    
%     disp('The sums of the passes are given by:')
%     
%     for i=1:cal4_inDS_tot_pass
%         
%     disp(sum(cal4_inDS_c1pass(i,:)))
%     %disp(sum(cal2_outDS_c1pass(i,:)))
%     
%     end
      
else
    disp('No degree-sequences pass condition 1')
end

disp('######################################################################')

%plots(k, p_in,p_out,P_in,P_out,PL_in_rv, PL_out_rv);

toc

end