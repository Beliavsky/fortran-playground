! Independent MIT consumer; see licenses/pareto-diis-drivers-MIT.txt.
module manufactured_jacobi_system
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   real(real64), allocatable :: a(:,:)
   integer :: offdiag_calls=0,diagonal_calls=0,norm_calls=0
contains
   subroutine offdiagonal(n,x,y)
      integer, intent(in) :: n
      real(real64), intent(in) :: x(n)
      real(real64), intent(out) :: y(n)
      integer :: i,j
      y=0
      do i=1,n
         do j=1,n
            if (i/=j) y(i)=y(i)+a(i,j)*x(j)
         end do
      end do
      offdiag_calls=offdiag_calls+1
   end subroutine
   subroutine inverse_diagonal(n,x,y)
      integer, intent(in) :: n
      real(real64), intent(in) :: x(n)
      real(real64), intent(out) :: y(n)
      integer :: i
      do i=1,n
         y(i)=x(i)/a(i,i)
      end do
      diagonal_calls=diagonal_calls+1
   end subroutine
   real(real64) function custom_norm(n,x) result(value)
      integer, intent(in) :: n
      real(real64), intent(in) :: x(n)
      value=maxval(abs(x))
      norm_calls=norm_calls+1
   end function
end module

program jacobi_reference
   use manufactured_jacobi_system
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   interface
      subroutine jacobi_diis(n,lprint,diis_max,norm,tol,rhs,x,n_iter,ok,matvec,dm1vec,u_norm)
         import real64
         integer, intent(in) :: n,lprint,diis_max,norm
         real(real64), intent(in) :: tol,rhs(n)
         real(real64), intent(inout) :: x(n)
         integer, intent(inout) :: n_iter
         logical, intent(inout) :: ok
         external :: matvec,dm1vec
         real(real64), external, optional :: u_norm
      end subroutine
   end interface
   integer, parameter :: sizes(*)=[3,7,13],histories(*)=[0,4]
   real(real64), allocatable :: b(:),x(:),exact(:)
   real(real64) :: residue,error,worst_error,worst_residual,value,row_sum
   integer :: sz,n,pattern,solution_pattern,guess,mode,history,i,j,iterations,runs,entries,custom_runs
   logical :: converged
   runs=0; entries=0; custom_runs=0; worst_error=0; worst_residual=0
   do sz=1,size(sizes)
      n=sizes(sz); allocate(a(n,n),b(n),x(n),exact(n))
      do pattern=1,2
         a=0
         do i=1,n
            do j=1,n
               if (i==j) cycle
               if (pattern==1) then
                  a(i,j)=real(modulo(i+j,5)-2,real64)/16
               else
                  a(i,j)=real(modulo(3*i-2*j,7)-3,real64)/16
               end if
            end do
            row_sum=sum(abs(a(i,:)))
            a(i,i)=2+i/4.0_real64+2*row_sum
         end do
         do solution_pattern=1,2
            do i=1,n
               if (solution_pattern==1) then
                  exact(i)=real(modulo(3*i,11)-5,real64)/4
               else
                  exact(i)=1.0_real64/(i+1)
               end if
            end do
            ! Assemble a manufactured right-hand side without calling either solver callback.
            do i=1,n
               value=0
               do j=1,n
                  value=value+a(i,j)*exact(j)
               end do
               b(i)=value
            end do
            do guess=1,2
               do mode=1,4
                  do history=1,size(histories)
                     x=0
                     if (guess==2) x=[(real(modulo(i,3)-1,real64),i=1,n)]
                     offdiag_calls=0; diagonal_calls=0; norm_calls=0
                     iterations=300; converged=.false.
                     call jacobi_diis(n,0,histories(history),mode,1.e-11_real64,b,x,iterations,converged, &
                        offdiagonal,inverse_diagonal,custom_norm)
                     if (.not.converged .or. iterations>300) error stop 'Jacobi/DIIS did not converge'
                     if (.not.all(ieee_is_finite(x))) error stop 'nonfinite Jacobi/DIIS solution'
                     if (offdiag_calls<=0 .or. diagonal_calls<=0) error stop 'solver callbacks unused'
                     if (mode==4) then
                        if (norm_calls<=0) error stop 'custom norm unused'
                        custom_runs=custom_runs+1
                     else
                        if (norm_calls/=0) error stop 'unexpected custom norm use'
                     end if
                     error=maxval(abs(x-exact))/(1+maxval(abs(exact)))
                     residue=maxval(abs(matmul(a,x)-b))/(1+maxval(abs(b)))
                     if (error>2.e-9_real64) error stop 'manufactured Jacobi/DIIS solution differs'
                     if (residue>2.e-10_real64) error stop 'independent Jacobi/DIIS residual'
                     worst_error=max(worst_error,error); worst_residual=max(worst_residual,residue)
                     runs=runs+1; entries=entries+n
                  end do
               end do
            end do
         end do
      end do
      deallocate(a,b,x,exact)
   end do
   if (runs/=192 .or. entries/=1472 .or. custom_runs/=48) error stop 'Jacobi/DIIS reference counts'
   print '(a,i0,a,i0)', 'Manufactured linear systems: ',runs,'; scalar solution references: ',entries
   print '(a,2es14.5)', 'Maximum normalized solution error and true residual: ',worst_error,worst_residual
   print '(a)', 'Symmetric/nonsymmetric diagonal dominance; two guesses, four norm modes, Jacobi and DIIS(4).'
   print '(a)', 'Off-diagonal and inverse-diagonal callbacks checked; molecular coupling and forces unverified here.'
   print '(a)', 'PASS ddpcm-jacobi-reference'
end program
