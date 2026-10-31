! Independent API consumer; see licenses/gmres-inverse-drivers-MIT.txt.
program checked_lightkrylov
   use LightKrylov, only: dense_linop_rdp,dense_vector_rdp,dense_vector,gmres,gmres_dp_opts,gmres_dp_metadata
   use LightKrylov_Constants, only: dp
   use LightKrylov_Logger, only: logger_setup
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(4)=[2,5,8,13]
   integer :: s,pattern,rhs,trans,guess,restart,solves=0,entries=0,restarted=0
   real(dp) :: worst_error=0,worst_residual=0
   call logger_setup(log_level=40,log_stdout=.false.,log_timestamp=.false.)
   do s=1,4
      do pattern=1,3
         do rhs=1,3
            do trans=0,1
               do guess=1,2
                  do restart=1,2
                     call fixture(sizes(s),pattern,rhs,trans,guess,restart)
                  end do
               end do
            end do
         end do
      end do
   end do
   if (restarted<1) error stop 'restart cycles not exercised'
   print '(a,i0)', 'GMRES solves: ',solves
   print '(a,i0)', 'Known solution entries: ',entries
   print '(a,i0)', 'Solves requiring multiple outer cycles: ',restarted
   print '(a,es12.4)', 'Maximum normalized solution error: ',worst_error
   print '(a,es12.4)', 'Maximum scaled true residual: ',worst_residual
   print '(a)', 'PASS lightkrylov-gmres-reference'
contains
   subroutine fixture(n,pattern,rhs,trans,guess,restart)
      integer, intent(in) :: n,pattern,rhs,trans,guess,restart
      type(dense_linop_rdp) :: operator
      type(dense_vector_rdp) :: b,x
      type(gmres_dp_opts) :: options
      type(gmres_dp_metadata) :: meta
      real(dp) :: a(n,n),effective(n,n),truth(n),right(n),start(n),value,error,residual,denominator
      integer :: i,j,info
      a=0
      do i=1,n
         do j=1,n
            select case(pattern)
            case(1)
               if (i/=j) a(i,j)=real(mod(7*i+3*j,11)-5,dp)/16
            case(2)
               if (j==i+1) a(i,j)=0.5_dp
               if (i==j+1) a(i,j)=-0.125_dp
            case(3)
               if (abs(i-j)==1) a(i,j)=-1
            end select
         end do
         if (pattern==1) a(i,i)=1+sum(abs(a(i,:)))
         if (pattern==2) a(i,i)=1+real(i,dp)/n
         if (pattern==3) a(i,i)=2
         select case(rhs)
         case(1)
            truth(i)=1
         case(2)
            truth(i)=real((-1)**i*i,dp)/8
         case(3)
            truth(i)=real(i*(n+1-i),dp)/4
         end select
      end do
      effective=a
      if (trans==1) then
         do j=1,n
            do i=1,n
               effective(i,j)=a(j,i)
            end do
         end do
      end if
      right=0
      do i=1,n
         do j=1,n
            right(i)=right(i)+effective(i,j)*truth(j)
         end do
      end do
      start=0
      if (guess==2) start=-0.25_dp
      operator%data=a; b=dense_vector(right); x=dense_vector(start)
      options%kdim=n
      if (restart==2) options%kdim=min(3,n)
      options%maxiter=500
      call gmres(operator,b,x,info,rtol=1e-10_dp,atol=1e-12_dp,options=options,transpose=trans==1,meta=meta)
      if (info<0.or..not.meta%converged) error stop 'GMRES convergence status'
      if (.not.allocated(x%data)) error stop 'missing solution'
      if (size(x%data)/=n) error stop 'solution dimension'
      if (.not.all(ieee_is_finite(x%data))) error stop 'nonfinite solution'
      if (any(operator%data/=a).or.any(b%data/=right)) error stop 'operator or RHS changed'
      error=maxval(abs(x%data-truth)/(1+abs(truth)))
      denominator=maxval(sum(abs(effective),dim=2))*maxval(abs(x%data))+maxval(abs(right))
      residual=0
      do i=1,n
         value=-right(i)
         do j=1,n
            value=value+effective(i,j)*x%data(j)
         end do
         residual=max(residual,abs(value)/denominator)
      end do
      worst_error=max(worst_error,error); worst_residual=max(worst_residual,residual)
      if (error>5e-8_dp.or.residual>2e-10_dp) error stop 'known solution/true residual mismatch'
      if (meta%n_outer>1) restarted=restarted+1
      solves=solves+1; entries=entries+n
   end subroutine fixture
end program checked_lightkrylov
