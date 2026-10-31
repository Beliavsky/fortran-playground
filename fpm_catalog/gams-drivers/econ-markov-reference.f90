! Independent API consumer; see licenses/resampling-markov-drivers-MIT.txt.
program markov_reference
   use shared_mod, only: wp
   use dist_mod, only: markov_steady_state, tauchen
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: tol = 1.e-11_wp
   real(wp) :: reset(3,3), expected(3), stationary(3)
   integer :: j
   call two_state(.1_wp, .2_wp)
   call two_state(.7_wp, .6_wp)
   call two_state(.02_wp, .03_wp)
   expected = [.1_wp, .3_wp, .6_wp]
   do j = 1, 3
      reset(:,j) = expected
   end do
   call solve(reset, stationary)
   if (maxval(abs(stationary-expected)) > tol) error stop 'rank-one equilibrium'
   print '(a,3f10.6)', 'Three-state reset equilibrium:', stationary
   call ar1(0._wp, 0._wp, .2_wp)
   call ar1(1.5_wp, .8_wp, .1_wp)
   call ar1(-.7_wp, -.5_wp, .3_wp)
   print '(a)', 'PASS econ-markov-reference'
contains
   subroutine solve(matrix, p)
      real(wp), intent(in) :: matrix(:,:)
      real(wp), intent(out) :: p(:)
      integer :: status
      p = 0._wp
      call markov_steady_state(matrix, p, 1.e-14_wp, 10000, status)
      if (status /= 0) error stop 'stationary iteration did not converge'
      if (.not. all(ieee_is_finite(p))) error stop 'nonfinite equilibrium'
      if (minval(p) < 0._wp .or. abs(sum(p)-1._wp) > tol) error stop 'invalid stationary probabilities'
      if (maxval(abs(matmul(matrix,p)-p)) > tol) error stop 'stationary equation residual'
   end subroutine solve

   subroutine two_state(a, b)
      real(wp), intent(in) :: a, b
      real(wp) :: matrix(2,2), p(2), exact(2)
      ! Column-stochastic convention: probability flow 1->2 is a, 2->1 is b.
      matrix(:,1) = [1._wp-a, a]
      matrix(:,2) = [b, 1._wp-b]
      exact = [b, a]/(a+b)
      call solve(matrix, p)
      if (maxval(abs(p-exact)) > tol) error stop 'analytic two-state equilibrium'
      print '(a,2f7.3,a,2f10.6)', 'a,b=', a, b, ' equilibrium=', p
   end subroutine two_state

   subroutine ar1(mu, rho, sigma)
      real(wp), intent(in) :: mu, rho, sigma
      integer, parameter :: n = 31
      real(wp), parameter :: width = 3._wp
      real(wp) :: nodes(n), transition(n,n), exact_nodes(n), reference(n,n), p(n)
      real(wp) :: extent, conditional_mean, lower, upper, step, probability_error
      integer :: i, k
      call tauchen(n, mu, rho, sigma, width, nodes, transition)
      if (.not. all(ieee_is_finite(nodes))) error stop 'nonfinite AR nodes'
      if (.not. all(ieee_is_finite(transition))) error stop 'nonfinite AR probabilities'
      extent = width*sigma/sqrt(1._wp-rho*rho)
      do k = 1, n
         exact_nodes(k) = mu + extent*(real(2*(k-1),wp)/(n-1)-1._wp)
      end do
      if (maxval(abs(nodes-exact_nodes)) > tol) error stop 'AR grid endpoints and spacing'
      ! Integrate the conditional normal density over midpoint cells, including tails.
      do i = 1, n
         conditional_mean = mu + rho*(exact_nodes(i)-mu)
         do k = 1, n
            lower = 0._wp
            upper = 1._wp
            if (k > 1) then
               step = (exact_nodes(k-1)+exact_nodes(k))/2._wp
               lower = .5_wp*(1._wp+erf((step-conditional_mean)/(sqrt(2._wp)*sigma)))
            end if
            if (k < n) then
               step = (exact_nodes(k)+exact_nodes(k+1))/2._wp
               upper = .5_wp*(1._wp+erf((step-conditional_mean)/(sqrt(2._wp)*sigma)))
            end if
            reference(i,k) = upper-lower
         end do
      end do
      probability_error = maxval(abs(transition-reference))
      if (probability_error > tol) error stop 'independent normal cell probabilities'
      if (minval(transition) < 0._wp) error stop 'negative transition probability'
      if (maxval(abs(sum(transition,dim=2)-1._wp)) > tol) error stop 'transition rows must sum to one'
      ! tauchen returns ROW probabilities; steady_state expects COLUMN probabilities.
      call solve(transpose(transition), p)
      if (abs(dot_product(p,nodes)-mu) > tol) error stop 'symmetric AR stationary mean'
      if (rho == 0._wp) then
         if (maxval(abs(p-reference(1,:))) > tol) error stop 'independent identically distributed equilibrium'
      end if
      print '(a,f5.2,a,f6.2,a,es10.2)', 'AR rho=', rho, ' mean=', dot_product(p,nodes), &
         ' maximum probability error=', probability_error
   end subroutine ar1
end program markov_reference
