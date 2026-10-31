! Independent API consumer; MIT: licenses/kriging-network-drivers-MIT.txt.
program kriging_reference
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: dp = real64
   real(dp), parameter :: positions(*) = [-1._dp,0._dp,.5_dp,1._dp,1.5_dp,2._dp,3._dp]
   real(dp), parameter :: distances(*) = [0._dp,.5_dp,1._dp,2._dp,3._dp,4._dp]
   real(dp) :: rotation(1,3,3),matrix(3,3),packed(6),rhs(3),original_rhs(3),weights(3)
   real(dp) :: r,c1,c2,expected(3),analytic(3),estimate,variance,variance_ref,residual,total
   real(dp) :: estimates(size(positions)),variances(size(positions))
   real :: nugget(1),sill(1),parameter(1),cmax,covariance
   integer :: nested(1),model(1),i,j,k,tag,q,status,solves
   interface
      subroutine cova3(x1,y1,z1,x2,y2,z2,ivarg,nst,maxnst,c0,it,cc,aa,irot,maxrot,rotmat,cmax,cova)
         import dp
         real :: x1,y1,z1,x2,y2,z2,c0(*),cc(*),aa(*),cmax,cova
         integer :: ivarg,nst(*),maxnst,it(*),irot,maxrot
         real(dp) :: rotmat(maxrot,3,3)
      end subroutine cova3
      subroutine ksol(nright,neq,nsb,a,r,s,ising)
         import dp
         integer :: nright,neq,nsb,ising
         real(dp) :: a(*),r(*),s(*)
      end subroutine ksol
   end interface
   rotation = 0._dp
   do i = 1,3
      rotation(1,i,i) = 1._dp
   end do
   nested = 1
   nugget = 0.
   sill = 1.
   parameter = 3.
   solves = 0
   do tag = 1,3
      model = tag
      do i = 1,size(distances)
         r = observed_covariance(distances(i))
         if (abs(r-kernel(distances(i),tag)) > 2.e-7_dp) error stop 'covariance model reference'
      end do
      r = observed_covariance(2._dp)
      matrix = reshape([1._dp,r,1._dp, r,1._dp,1._dp, 1._dp,1._dp,0._dp],[3,3])
      do q = 1,size(positions)
         c1 = observed_covariance(abs(positions(q)))
         c2 = observed_covariance(abs(positions(q)-2._dp))
         if (abs(c1-kernel(abs(positions(q)),tag)) > 2.e-7_dp) error stop 'left target covariance'
         if (abs(c2-kernel(abs(positions(q)-2._dp),tag)) > 2.e-7_dp) error stop 'right target covariance'
         rhs = [c1,c2,1._dp]
         original_rhs = rhs
         k = 0
         do j = 1,3
            do i = 1,j
               k = k+1
               packed(k) = matrix(i,j)
            end do
         end do
         call ksol(1,3,1,packed,rhs,weights,status)
         if (status /= 0) error stop 'kriging linear solve status'
         if (.not. all(ieee_is_finite(weights))) error stop 'nonfinite kriging weights'
         expected = closed_weights(r,c1,c2)
         if (maxval(abs(weights-expected)) > 1.e-11_dp) error stop 'closed weights for rounded covariances'
         if (abs(sum(weights(:2))-1._dp) > 1.e-11_dp) error stop 'ordinary kriging unbiasedness'
         residual = 0._dp
         do i = 1,3
            total = -original_rhs(i)
            do j = 1,3
               total = total+matrix(i,j)*weights(j)
            end do
            residual = max(residual,abs(total))
         end do
         if (residual > 1.e-11_dp) error stop 'independent kriging system residual'
         analytic = closed_weights(kernel(2._dp,tag),kernel(abs(positions(q)),tag), &
            kernel(abs(positions(q)-2._dp),tag))
         if (maxval(abs(weights-analytic)) > 5.e-7_dp) error stop 'end-to-end analytic weights'
         estimate = weights(1)+3*weights(2)
         variance = 1._dp-sum(weights(:2)*original_rhs(:2))-weights(3)
         variance_ref = 1._dp-analytic(1)*kernel(abs(positions(q)),tag) &
            -analytic(2)*kernel(abs(positions(q)-2._dp),tag)-analytic(3)
         if (.not. all(ieee_is_finite([estimate,variance]))) error stop 'nonfinite kriging outputs'
         if (abs(estimate-(analytic(1)+3*analytic(2))) > 1.e-6_dp) error stop 'analytic kriging estimate'
         if (variance < -1.e-11_dp .or. abs(variance-variance_ref) > 1.e-6_dp) error stop 'analytic kriging variance'
         if (abs(5*sum(weights(:2))-5._dp) > 1.e-11_dp) error stop 'constant field reproduction'
         estimates(q) = estimate
         variances(q) = variance
         solves = solves+1
         print '(a,i0,a,f5.1,a,f11.7,a,f11.7)', 'Model=',tag,' x=',positions(q), &
            ' estimate=',estimate,' variance=',variance
      end do
      if (abs(estimates(2)-1._dp) > 1.e-11_dp .or. abs(estimates(6)-3._dp) > 1.e-11_dp) &
         error stop 'observation interpolation'
      if (abs(estimates(4)-2._dp) > 1.e-11_dp) error stop 'symmetric midpoint estimate'
      do q = 1,size(positions)
         if (abs(estimates(q)+estimates(size(positions)+1-q)-4._dp) > 1.e-11_dp) error stop 'estimate reflection'
         if (abs(variances(q)-variances(size(positions)+1-q)) > 1.e-11_dp) error stop 'variance reflection'
      end do
   end do
   if (solves /= 21) error stop 'kriging solve count'
   print '(a)', 'Three covariance kernels and 21 two-observation ordinary kriging systems checked.'
   print '(a)', 'PASS gslib-kriging-reference'
contains
   real(dp) function observed_covariance(distance) result(value)
      real(dp), intent(in) :: distance
      call cova3(0.,0.,0.,real(distance),0.,0.,1,nested,1,nugget,model,sill,parameter,1,1,rotation,cmax,covariance)
      if (.not. all(ieee_is_finite([cmax,covariance]))) error stop 'nonfinite covariance'
      if (cmax /= 1.) error stop 'unit sill'
      value = real(covariance,dp)
   end function observed_covariance
   real(dp) function kernel(distance,tag) result(value)
      real(dp), intent(in) :: distance
      integer, intent(in) :: tag
      real(dp) :: t
      t = distance/3
      select case(tag)
      case(1)
         value = 0._dp
         if (t < 1._dp) value = 1._dp-1.5_dp*t+.5_dp*t**3
      case(2)
         value = exp(-distance)
      case(3)
         value = exp(-distance*distance/3)
      end select
   end function kernel
   function closed_weights(r,c1,c2) result(w)
      real(dp), intent(in) :: r,c1,c2
      real(dp) :: w(3)
      w(1) = .5_dp*(1._dp+(c1-c2)/(1._dp-r))
      w(2) = 1._dp-w(1)
      w(3) = c1-w(1)-r*w(2)
   end function closed_weights
end program kriging_reference
