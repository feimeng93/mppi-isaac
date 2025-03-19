clc; clear all; close all
%% Uncertain Obstacle : Eq(4)
syms x y z w
% obstacle g(x1,x2,w)>=0 where w is probabilistic uncertainty
g= -((5*(x))^2+(9/4)*(5*y)^2+(5*z)^2-1)^3+(5*(x))^2*(5*z)^3+(9/80)*(5*y)^2*(5*z)^3+w;
dg=polynomialDegree(g);%max degree of polynomial g

% w: uncertain parameter w~Uniform(l,u)
% u=0.1;l=-0.1; m_w=[1];for i=1:2*dg ;m_w(i+1,1)=(1/(u-l))*((u^(i+1) - l^(i+1))/(i+1));end
mean=0.05; var=0.01; for k=0:2*dg; m_w(k+1,1)=sqrt(var)^k*(-j*sqrt(2))^k*kummerU(-k/2, 1/2,-1/2*mean^2/var);end

%% Calculate the first and Second order moments of new random variable z=g(x1,x2,w)
Mg=[]; %list of first and second order moments of z in Eq(21)
for dd=1:2
% Moment of order dd of z
Md=expand(g^dd);
% replace moments of uncertain parameter w
Md1=subs(Md,flip(w.^[1:dd*dg].'),flip(m_w(2:dd*dg+1))) ; 
Mg=[Mg;Md1];

end
%% Inner approximation of Static Delta-risk contour in Eq(10)

Cons_1=(Mg(2)-Mg(1)^2)/Mg(2);
Cons_2=Mg(1);

clc;display('Done!');display('Working on plots!')

%% Plot

[x,y,z]=meshgrid([-1.5:0.02:1.5],[-1.5:0.02:1.5],[-1.5:0.02:1.5]);
P=eval(Cons_1);
risk_level=[0.01,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9];
for n=1:10
figure(n); 
hold on
Delta = risk_level(n);
vertices_faces=isosurface(x,y,z,P,Delta);
patch_num = patch(vertices_faces);
normal=isonormals(x,y,z,P,patch_num);

set(patch_num,'FaceColor','green','EdgeColor','none','FaceAlpha',1); % red
lighting phong; view(3); axis tight vis3d; camlight ;axis normal

% Delta=0.3;h = patch(isosurface(x1,x2,x3,P,Delta));
% isonormals(x1,x2,x3,P,h);set(h,'FaceColor','black','EdgeColor','none','FaceAlpha',0.4); % red
% lighting phong; view(3); axis tight vis3d; camlight ;axis normal
% 
% Delta=0.1;h = patch(isosurface(x1,x2,x3,P,Delta));
% isonormals(x1,x2,x3,P,h);set(h,'FaceColor','blue','EdgeColor','none','FaceAlpha',0.3); % red
% lighting phong; view(3); axis tight vis3d; camlight ;axis normal
% 
% 
% Delta=0.05;h = patch(isosurface(x1,x2,x3,P,Delta));
% isonormals(x1,x2,x3,P,h);set(h,'FaceColor','red','EdgeColor','none','FaceAlpha',0.1); % red
% lighting phong; view(3); axis tight vis3d; camlight ;axis normal


grid on; axis square; set(gca,'fontsize',25);xlim([-1.5 1.5]);ylim([-1.5 1.5]);zlim([-1.5 1.5])
xlabel('$x_1$','Interpreter','latex', 'FontSize',25); ylabel('$x_2$','Interpreter','latex', 'FontSize',25);view(-72,10)
mkdir(sprintf('./heart2_contour_data'));
save(sprintf('./heart2_contour_data/vertices_faces_%d.mat',n-1),'vertices_faces')
save(sprintf('./heart2_contour_data/patch_%d.mat',n-1),'patch_num')
save(sprintf('./heart2_contour_data/normal_%d.mat',n-1),'normal')
end
