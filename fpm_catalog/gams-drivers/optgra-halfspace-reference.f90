! Independent MIT-licensed driver; see licenses/projection-training-drivers-MIT.txt.
module halfspace_fixture
   use optgra_module, only: optgra, wp => optgra_wp
   implicit none
   real(wp), allocatable :: center(:), normal(:), diagonal(:)
   real(wp) :: height
   integer :: value_calls, derivative_calls
contains
   subroutine values(me,x,c,flag)
      class(optgra), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: c(:)
      integer, intent(in) :: flag
      value_calls=value_calls+1
      c(1)=sum(normal*(x-center))-height
      c(2)=0.5_wp*sum(diagonal*(x-center)**2)
   end subroutine
   subroutine derivatives(me,x,c,jac)
      class(optgra), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: c(:),jac(:,:)
      derivative_calls=derivative_calls+1
      call values(me,x,c,0)
      jac(1,:)=normal
      jac(2,:)=diagonal*(x-center)
   end subroutine
end module

program reference_halfspace
   use halfspace_fixture
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(optgra) :: solver
   integer, parameter :: dims(3)=[2,3,5]
   integer :: dn,n,cond,ih,shift,start,i,status,iterations,units(3),runs,entries,calls
   real(wp), allocatable :: x(:),exact(:),offset(:),scales(:),perturb(:)
   integer, allocatable :: lengths(:),types(:)
   character(len=80), allocatable :: names(:)
   character(len=80) :: cnames(2)
   real(wp) :: c(2),den,multiplier,fstar,point_error,objective_error,feasibility,kkt,identity
   real(wp) :: max_point,max_objective,max_feasibility,max_kkt,max_identity
   runs=0; entries=0; calls=0
   max_point=0; max_objective=0; max_feasibility=0; max_kkt=0; max_identity=0
   cnames=[character(len=80) :: 'halfspace','objective']
   do i=1,3
      open(newunit=units(i),status='scratch',action='readwrite')
   end do
   do dn=1,size(dims)
      n=dims(dn)
      allocate(center(n),normal(n),diagonal(n),x(n),exact(n),offset(n),scales(n),perturb(n))
      allocate(lengths(n),types(n),names(n))
      scales=1; perturb=1e-5_wp; lengths=1; types=0; names='x'
      do cond=1,5,4
         do i=1,n
            diagonal(i)=1+real(cond-1,wp)*real(i-1,wp)/real(n-1,wp)
            normal(i)=(-1.0_wp)**i*(1+real(i,wp)/4)
         end do
         den=sum(normal**2/diagonal)
         do ih=1,2
            height=0.5_wp
            if (ih==2) height=2.0_wp
            multiplier=height/den
            offset=multiplier*normal/diagonal
            fstar=height**2/(2*den)
            do shift=0,1
               center=[(real(shift*(i-2),wp)/4,i=1,n)]
               exact=center+offset
               do start=0,1
                  x=center+2*real(start,wp)*offset
                  value_calls=0; derivative_calls=0
                  ! Consca contains stopping thresholds, not unit scale factors.
                  call solver%initialize(n,1,values,derivatives,[1e-5_wp,1e-5_wp],[1,1], &
                     [1e-9_wp,1e-11_wp],cnames,[9,9],[1,-1],1,perturb,1.0_wp,1.0_wp, &
                     300,30,20,20,20,units(1),0,0,scales,names,lengths,types,units(2),0,0,units(3),0,2)
                  call solver%solve(x,c,status,iterations)
                  if (status/=1) then
                     print *, 'Failure n,condition,height,shift,start,status:',n,cond,height,shift,start,status
                     error stop 'Optgra did not report a feasible optimum'
                  end if
                  if (.not.all(ieee_is_finite(x)) .or. .not.all(ieee_is_finite(c))) error stop 'nonfinite result'
                  if (derivative_calls<=0 .or. value_calls<=0) error stop 'callbacks not exercised'
                  point_error=maxval(abs(x-exact))/(1+maxval(abs(exact)))
                  objective_error=abs(0.5_wp*sum(diagonal*(x-center)**2)-fstar)/(1+fstar)
                  feasibility=max(0.0_wp,height-sum(normal*(x-center)))/(1+height)
                  kkt=maxval(abs(diagonal*(x-center)-multiplier*normal))/(1+maxval(abs(multiplier*normal)))
                  identity=max(abs(c(1)-(sum(normal*(x-center))-height))/(1+height), &
                     abs(c(2)-0.5_wp*sum(diagonal*(x-center)**2))/(1+fstar))
                  if (point_error>2e-4_wp .or. objective_error>1e-7_wp) error stop 'analytic optimum mismatch'
                  if (feasibility>2e-7_wp .or. kkt>2e-4_wp) error stop 'independent KKT check failed'
                  if (identity>1e-8_wp) error stop 'returned values disagree with direct evaluation'
                  max_point=max(max_point,point_error); max_objective=max(max_objective,objective_error)
                  max_feasibility=max(max_feasibility,feasibility); max_kkt=max(max_kkt,kkt)
                  max_identity=max(max_identity,identity)
                  calls=calls+derivative_calls; runs=runs+1; entries=entries+n
                  call solver%destroy()
               end do
            end do
         end do
      end do
      deallocate(center,normal,diagonal,x,exact,offset,scales,perturb,lengths,types,names)
   end do
   do i=1,3
      close(units(i))
   end do
   print '(a,i0,a,i0)', 'Halfspace projections: ',runs,'; analytic coordinates: ',entries
   print '(a,i0)', 'Analytic derivative callbacks: ',calls
   print '(a,5es14.5)', 'Max point, objective, feasibility, KKT, returned-value errors: ', &
      max_point,max_objective,max_feasibility,max_kkt,max_identity
   print '(a)', 'PASS optgra-halfspace-reference'
end program
