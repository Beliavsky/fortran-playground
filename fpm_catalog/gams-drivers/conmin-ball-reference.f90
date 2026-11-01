! Independent MIT-licensed driver; see licenses/directions-fitting-drivers-MIT.txt.
program reference_feasible_directions
   use conmin_module, only: conmin_class,wp => conmin_wp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: dims(3)=[2,3,5]
   integer :: dn,n,rad,shift,direction,start,runs,entries,gradient_calls,total_gradients
   real(wp), allocatable :: center(:),target(:),exact(:),d(:)
   real(wp) :: radius,point_error,objective_error,feasibility,kkt,identity
   real(wp) :: max_point,max_objective,max_feasibility,max_kkt,max_identity
   runs=0; entries=0; total_gradients=0
   max_point=0; max_objective=0; max_feasibility=0; max_kkt=0; max_identity=0
   do dn=1,size(dims)
      n=dims(dn)
      allocate(center(n),target(n),exact(n),d(n))
      do rad=1,2
         radius=0.5_wp
         if (rad==2) radius=2.0_wp
         do shift=0,1
            block
               integer :: j
               center=[(real(shift*(j-2),wp)/4,j=1,n)]
            end block
            do direction=1,2
               block
                  integer :: j
                  d=[((-1.0_wp)**(direction*j)*real(j,wp),j=1,n)]
               end block
               d=d/sqrt(sum(d*d))
               target=center+2*radius*d
               exact=center+radius*d
               do start=0,1
                  call solve_fixture()
               end do
            end do
         end do
      end do
      deallocate(center,target,exact,d)
   end do
   print '(a,i0,a,i0)', 'Ball projections: ',runs,'; analytic coordinates: ',entries
   print '(a,i0)', 'User-gradient requests: ',total_gradients
   print '(a,5es14.5)', 'Max point, objective, feasibility, KKT, returned-objective errors: ', &
      max_point,max_objective,max_feasibility,max_kkt,max_identity
   print '(a)', 'PASS conmin-ball-reference'
contains
   subroutine solve_fixture()
      type(conmin_class) :: solver
      integer :: n1,n2,n3,n4,n5,request
      real(wp) :: x(n+2),lower(n+2),upper(n+2),g(1+2*n),scal(n+2),df(n+2),a(n+2,n+2)
      real(wp) :: s(n+2),g1(1+2*n),g2(1+2*n),b(n+2,n+2),c(n+2),y(n),actual_f,actual_g
      integer :: isc(1+2*n),ic(n+2),ms1(2*(n+2))
      n1=n+2; n2=1+2*n; n3=n+2; n4=n+2; n5=2*n4
      x=0; lower=-100; upper=100; scal=1; g=0; df=0; a=0
      s=0; g1=0; g2=0; b=0; c=0; isc=0; ic=0; ms1=0
      ! Add a perpendicular component so neither start lies on the target ray.
      x(1:n)=center+(0.25_wp+real(start,wp))*radius*d
      y=-d(1)*d; y(1)=y(1)+1
      x(1:n)=x(1:n)+0.1_wp*radius*y/sqrt(sum(y*y))
      solver%ndv=n; solver%ncon=1; solver%nside=0
      solver%infog=0; solver%info=0; solver%nfdg=1; solver%iprint=0
      solver%itmax=300; solver%icndir=0; solver%nscal=0; solver%itrm=3
      solver%ct=-0.01_wp*radius**2; solver%ctmin=1e-9_wp*radius**2
      solver%delfun=1e-12_wp; solver%dabfun=1e-12_wp
      solver%igoto=0; gradient_calls=0
      do request=1,10000
         call solver%solve(x,lower,upper,g,scal,df,a,s,g1,g2,b,c,isc,ic,ms1,n1,n2,n3,n4,n5)
         if (solver%igoto==0) exit
         if (.not.all(ieee_is_finite(x(1:n)))) error stop 'nonfinite callback coordinates'
         y=x(1:n)-center
         select case(solver%info)
         case(1)
            solver%obj=0.5_wp*sum((x(1:n)-target)**2)
            g(1)=sum(y*y)-radius**2
         case(2)
            gradient_calls=gradient_calls+1
            solver%obj=0.5_wp*sum((x(1:n)-target)**2)
            df(1:n)=x(1:n)-target
            solver%nac=0
            if (g(1)>=solver%ct) then
               solver%nac=1; ic(1)=1; a(1:n,1)=2*y
            end if
         case default
            error stop 'unexpected reverse-communication request'
         end select
      end do
      if (solver%igoto/=0 .or. solver%iter>=solver%itmax) error stop 'iteration/request limit reached'
      if (gradient_calls<=0) error stop 'analytic derivatives not requested'
      if (.not.all(ieee_is_finite(x(1:n))) .or. .not.ieee_is_finite(solver%obj)) error stop 'nonfinite result'
      y=x(1:n)-center
      actual_f=0.5_wp*sum((x(1:n)-target)**2); actual_g=sum(y*y)-radius**2
      point_error=maxval(abs(x(1:n)-exact))/(1+maxval(abs(exact)))
      objective_error=abs(actual_f-0.5_wp*radius**2)/(1+0.5_wp*radius**2)
      feasibility=max(0.0_wp,actual_g)/(1+radius**2)
      ! The exact multiplier for g=norm(y)**2-R**2 <=0 is 1/2.
      kkt=maxval(abs((x(1:n)-target)+y))/(1+2*radius)
      identity=abs(solver%obj-actual_f)/(1+actual_f)
      print '(a,6i5,5es12.3)', 'Case: ',n,rad,shift,direction,start,solver%iter, &
         point_error,objective_error,feasibility,kkt,identity
      if (point_error>2e-4_wp .or. objective_error>2e-7_wp) error stop 'analytic minimizer mismatch'
      if (feasibility>2e-7_wp .or. kkt>2e-4_wp) error stop 'independent KKT check failed'
      if (identity>1e-8_wp) error stop 'returned objective differs'
      max_point=max(max_point,point_error); max_objective=max(max_objective,objective_error)
      max_feasibility=max(max_feasibility,feasibility); max_kkt=max(max_kkt,kkt); max_identity=max(max_identity,identity)
      total_gradients=total_gradients+gradient_calls; runs=runs+1; entries=entries+n
   end subroutine
end program
