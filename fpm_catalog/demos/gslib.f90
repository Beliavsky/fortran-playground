! Ordinary kriging from two observations using GSLIB covariance and solver routines.
! No data files: observations are value 1 at x=0 and value 3 at x=2.
program main
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64) :: rotation(1,3,3), a(6), rhs(3), weights(3), original_rhs(3)
   real(real64) :: matrix(3,3), corr, expected(3), residual, variance, estimate
   real :: c0(1), cc(1), ranges(1), cmax, covariance, point
   integer :: nst(1), model(1), i, j, k, status, sample
   interface
      subroutine cova3(x1,y1,z1,x2,y2,z2,ivarg,nst,maxnst,c0,it,cc,aa,irot,maxrot,rotmat,cmax,cova)
         import real64
         real :: x1,y1,z1,x2,y2,z2,c0(*),cc(*),aa(*),cmax,cova
         integer :: ivarg,nst(*),maxnst,it(*),irot,maxrot
         real(real64) :: rotmat(maxrot,3,3)
      end subroutine
      subroutine ksol(nright,neq,nsb,a,r,s,ising)
         import real64
         integer :: nright,neq,nsb,ising
         real(real64) :: a(*),r(*),s(*)
      end subroutine
   end interface

   ! Identity rotation; unit sill, zero nugget, exponential covariance exp(-h).
   rotation = 0._real64
   do i = 1, 3
      rotation(1,i,i) = 1._real64
   end do
   nst = 1
   model = 2
   c0 = 0.
   cc = 1.
   ranges = 3.
   call cova3(0.,0.,0.,2.,0.,0.,1,nst,1,c0,model,cc,ranges,1,1,rotation,cmax,covariance)
   corr = real(covariance,real64)
   if (abs(corr-exp(-2._real64)) > 2.e-7_real64) error stop 'Wrong covariance'
   matrix = reshape([1._real64,corr,1._real64,corr,1._real64,1._real64, &
                     1._real64,1._real64,0._real64],[3,3])
   print *, 'Position    Kriging estimate    Variance    System residual'
   do sample = 0, 4
      point = 0.5*sample
      do i = 1, 2
         call cova3(real(2*(i-1)),0.,0.,point,0.,0.,1,nst,1,c0,model,cc,ranges, &
                    1,1,rotation,cmax,covariance)
         rhs(i) = real(covariance,real64)
         if (abs(rhs(i)-exp(-abs(real(point,real64)-2*(i-1)))) > 2.e-7_real64) &
            error stop 'Wrong target covariance'
      end do
      rhs(3) = 1._real64
      original_rhs = rhs
      k = 0
      do j = 1, 3
         do i = 1, j
            k = k+1
            a(k) = matrix(i,j)
         end do
      end do
      call ksol(1,3,1,a,rhs,weights,status)
      if (status /= 0 .or. .not. all(ieee_is_finite(weights))) error stop 'Kriging solve failed'
      expected(1) = 0.5_real64*(1._real64+(original_rhs(1)-original_rhs(2))/(1._real64-corr))
      expected(2) = 1._real64-expected(1)
      expected(3) = original_rhs(1)-expected(1)-corr*expected(2)
      residual = maxval(abs(matmul(matrix,weights)-original_rhs))
      if (maxval(abs(weights-expected)) > 1.e-10_real64 .or. residual > 1.e-10_real64) &
         error stop 'Wrong kriging weights'
      estimate = weights(1)+3._real64*weights(2)
      variance = 1._real64-dot_product(weights(1:2),original_rhs(1:2))-weights(3)
      if (.not. ieee_is_finite(estimate) .or. variance < -1.e-10_real64) error stop 'Invalid estimate'
      if (sample == 0 .and. abs(estimate-1._real64) > 1.e-10_real64) error stop 'Endpoint mismatch'
      if (sample == 2 .and. abs(estimate-2._real64) > 1.e-10_real64) error stop 'Midpoint mismatch'
      if (sample == 4 .and. abs(estimate-3._real64) > 1.e-10_real64) error stop 'Endpoint mismatch'
      print '(f8.2,2f18.8,es18.3)', point, estimate, variance, residual
   end do
   print *, 'PASS gslib'
end program main
