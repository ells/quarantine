function [] = plots(k, p_in,p_out,P_in,P_out,PL_in_rv,PL_out_rv)

% Truncated PDF

figure

subplot(2,2,1)
plot(k,p_in(1,:),'b')
hold on
plot(k,p_out(1,:),'r')
axis([1 10 0 1])
title('In/out degree power law distributions, calibration 1')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2.8889','\alpha_{out}=2.1111')
hold off

subplot(2,2,2)
plot(k,p_in(2,:),'b')
hold on
plot(k,p_out(2,:),'r')
axis([1 10 0 1])
title('In/out degree power law distribution, calibration 2')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2.5556','\alpha_{out}=2.3333')
hold off

subplot(2,2,3)
plot(k,p_in(3,:),'b')
hold on
plot(k,p_out(3,:),'r')
axis([1 10 0 1])
title('In/out degree power law distributions,calibration 3')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2','\alpha_{out}=3')
hold off

subplot(2,2,4)
plot(k,p_in(4,:),'b')
hold on
plot(k,P_out(4,:),'r')
axis([1 10 0 1])
title('In/out degree power law distributions, calibration 4')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2.2222','\alpha_{out}=2.6667')
hold off

% Linearized truncated PDF

figure

subplot(2,2,1)
loglog(k,p_in(1,:),'b')
hold on
plot(k,p_out(1,:),'r')
axis([1 10 0 1])
title('In/out degree linearized PDFs, calibration 1')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2.8889','\alpha_{out}=2.1111')
hold off

subplot(2,2,2)
loglog(k,p_in(2,:),'b')
hold on
loglog(k,p_out(2,:),'r')
axis([1 10 0 1])
title('In/out degree  linearized PDFs, calibration 2')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2.5556','\alpha_{out}=2.3333')
hold off

subplot(2,2,3)
loglog(k,p_in(3,:),'b')
hold on
loglog(k,p_out(3,:),'r')
axis([1 10 0 1])
title('In/out degree  linearized PDFs,calibration 3')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2','\alpha_{out}=3')
hold off

subplot(2,2,4)
loglog(k,p_in(4,:),'b')
hold on
loglog(k,p_out(4,:),'r')
axis([1 10 0 1])
title('In/out degree  linearized PDFs, calibration 4')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2.2222','\alpha_{out}=2.6667')
hold off



% Truncated CDF

figure

subplot(2,2,1)
plot(k,P_in(1,:),'b')
hold on
plot(k,P_out(1,:),'r')
axis([1 10 0 1])
title('In/out degree CDF, calibration 1')
xlabel('k')
ylabel('P(k)')
legend('\alpha_{in}=2.8889','\alpha_{out}=2.1111')
hold off

subplot(2,2,2)
plot(k,P_in(2,:),'b')
hold on
plot(k,P_out(2,:),'r')
axis([1 10 0 1])
title('In/out degree CDF, calibration 2')
xlabel('k')
ylabel('P(k)')
legend('\alpha_{in}=2.5556','\alpha_{out}=2.3333')
hold off

subplot(2,2,3)
plot(k,P_in(3,:),'b')
hold on
plot(k,P_out(3,:),'r')
axis([1 10 0 1])
title('In/out degree CDF,calibration 3')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2','\alpha_{out}=3')
hold off

subplot(2,2,4)
plot(k,P_in(4,:),'b')
hold on
plot(k,P_out(4,:),'r')
axis([1 10 0 1])
title('In/out degree CDF, calibration 4')
xlabel('k')
ylabel('p(k)')
legend('\alpha_{in}=2.2222','\alpha_{out}=2.6667')
hold off

%Empirical CDF after Monte Carlo simulation

figure

%calibration 1

subplot(4,2,1)
hist(PL_in_rv(1,:),100)
title('Empirical in-degree distribution, calibration 1')
xlabel('k')
ylabel('f(k)')

subplot(4,2,2)
hist(PL_out_rv(1,:),100)
title('Empirical out-degree distribution, calibration 1')
xlabel('k')
ylabel('f(k)')

%calibration 2

subplot(4,2,3)
hist(PL_in_rv(2,:),100)
title('Empirical in-degree distribution, calibration 2')
xlabel('k')
ylabel('f(k)')

subplot(4,2,4)
hist(PL_out_rv(2,:),100)
title('Empirical out-degree distribution, calibration 2')
xlabel('k')
ylabel('f(k)')

%calibration 3


subplot(4,2,5)
hist(PL_in_rv(3,:),100)
title('Empirical in-degree distribution, calibration 3')
xlabel('k')
ylabel('f(k)')

subplot(4,2,6)
hist(PL_out_rv(3,:),100)
title('Empirical out-degree distribution, calibration 3')
xlabel('k')
ylabel('f(k)')

%calibration 4


subplot(4,2,7)
hist(PL_in_rv(4,:),100)
title('Empirical in-degree distribution, calibration ')
xlabel('k')
ylabel('f(k)')

subplot(4,2,8)
hist(PL_out_rv(4,:),100)
title('Empirical out-degree distribution, calibration 4')
xlabel('k')
ylabel('f(k)')


end

