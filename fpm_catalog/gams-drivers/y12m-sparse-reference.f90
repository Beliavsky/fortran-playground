! Independent API consumer; MIT: licenses/sparse-integral-drivers-MIT.txt.
program sparse_reference
   use y12m, only: y12mb, y12mc, y12md
   use, intrinsic :: iso_fortran_env, only: wp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n = 10
   real(wp) :: matrix(n,n), permuted(n,n)
   integer :: i
   matrix = 0._wp
   do i = 1,n
      matrix(i,i) = 4._wp+real(i,wp)/4
      if (i < n) then
         matrix(i,i+1) = -.5_wp
         matrix(i+1,i) = -1.25_wp
      end if
   end do
   matrix(1,n) = -.75_wp
   matrix(n,1) = .25_wp
   call check(matrix,1)
   ! A cyclic row permutation removes most diagonal pivots without changing the solution.
   do i = 1,n
      permuted(i,:) = matrix(mod(i,n)+1,:)
   end do
   call check(permuted,2)
   print '(a)', 'PASS y12m-sparse-reference'
contains
   subroutine check(original,case_number)
      real(wp), intent(in) :: original(n,n)
      integer, intent(in) :: case_number
      integer, parameter :: capacity = 1000
      real(wp) :: entries(capacity), pivot(n), rhs(n), b(n), exact(n), flags(8)
      real(wp) :: solution_error, backward_error, residual, denominator, row_norm
      integer :: columns(capacity), rows(capacity), ha(n,11), iflag(10), status, nz, i, j, load
      entries = 0._wp
      rows = 0
      columns = 0
      ha = 0
      nz = 0
      do i = 1,n
         do j = 1,n
            if (original(i,j) == 0._wp) cycle
            nz = nz+1
            entries(nz) = original(i,j)
            rows(nz) = i
            columns(nz) = j
         end do
      end do
      iflag = 0
      flags = 0._wp
      iflag(2:5) = [3,1,0,2]
      flags(1:4) = [16._wp,1.e-12_wp,1.e16_wp,1.e-12_wp]
      call y12mb(n,nz,entries,columns,capacity,rows,capacity,ha,n,flags,iflag,status)
      if (status /= 0) error stop 'sparse preparation status'
      do load = 1,4
         select case(load)
         case(1)
            exact = 1._wp
         case(2)
            exact = [(real((-1)**i*i,wp)/4,i=1,n)]
         case(3)
            exact = 0._wp
         case(4)
            exact = 0._wp
            exact(4) = 1._wp
         end select
         ! Preserve original A and form each manufactured RHS independently of sparse routines.
         rhs = 0._wp
         row_norm = 0._wp
         do i = 1,n
            do j = 1,n
               rhs(i) = rhs(i)+original(i,j)*exact(j)
            end do
            row_norm = max(row_norm,sum(abs(original(i,:))))
         end do
         b = rhs
         if (load == 1) then
            call y12mc(n,nz,entries,columns,capacity,rows,capacity,pivot,b,ha,n,flags,iflag,status)
            if (status /= 0) error stop 'sparse factorization status'
         else
            iflag(5) = 3
         end if
         call y12md(n,entries,capacity,b,pivot,columns,ha,n,iflag,status)
         if (status /= 0) error stop 'sparse substitution status'
         if (.not. all(ieee_is_finite(b))) error stop 'nonfinite sparse solution'
         solution_error = maxval(abs(b-exact))/max(1._wp,maxval(abs(exact)))
         backward_error = 0._wp
         do i = 1,n
            residual = -rhs(i)
            do j = 1,n
               residual = residual+original(i,j)*b(j)
            end do
            backward_error = max(backward_error,abs(residual))
         end do
         denominator = row_norm*maxval(abs(b))+maxval(abs(rhs))
         backward_error = backward_error/max(1._wp,denominator)
         if (solution_error > 1.e-11_wp) error stop 'known sparse solution'
         if (backward_error > 1.e-12_wp) error stop 'sparse backward error'
         print '(a,i0,a,i0,a,es10.2,a,es10.2)', 'Matrix ',case_number,', RHS ',load, &
            ' solution error=',solution_error,' backward error=',backward_error
      end do
      print '(a)', 'One sparse LU factorization reused for four right-hand sides.'
   end subroutine check
end program sparse_reference
