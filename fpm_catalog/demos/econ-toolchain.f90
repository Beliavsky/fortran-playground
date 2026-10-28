! Calls follow the author's test/markov_test.f90 and test/tauchen_test.f90 (MIT).
! markov_steady_state expects COLUMN-stochastic transitions.
! tauchen returns ROW-stochastic transitions, so transpose before iteration.
program main
   use shared_mod, only: wp
   use dist_mod, only: markov_steady_state, tauchen
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n = 31
   real(wp) :: transition(2,2), stationary(2), reference(2), residual
   real(wp) :: nodes(n), probabilities(n,n), distribution(n), mean, variance, exact_variance
   integer :: status

   transition(1,:) = [0.9_wp,0.2_wp]
   transition(2,:) = [0.1_wp,0.8_wp]
   stationary = 0._wp
   call markov_steady_state(transition,stationary,1.e-14_wp,10000,status)
   reference = [2._wp/3._wp,1._wp/3._wp]
   residual = maxval(abs(matmul(transition,stationary)-stationary))
   if (status /= 0 .or. .not. all(ieee_is_finite(stationary))) error stop 'Stationary iteration failed'
   if (maxval(abs(stationary-reference)) > 1.e-12_wp .or. residual > 1.e-12_wp) &
      error stop 'Wrong stationary distribution'
   print '(a,2f15.10)', 'Two-state equilibrium: ', stationary
   print '(a,es12.4)', 'Equilibrium residual: ', residual

   call tauchen(n,0._wp,0.8_wp,0.1_wp,3._wp,nodes,probabilities)
   if (.not. all(ieee_is_finite(probabilities))) error stop 'Nonfinite probability'
   if (minval(probabilities) < 0._wp .or. maxval(abs(sum(probabilities,dim=2)-1._wp)) > 1.e-12_wp) &
      error stop 'Invalid transition probabilities'
   distribution = 0._wp
   call markov_steady_state(transpose(probabilities),distribution,1.e-14_wp,10000,status)
   if (status /= 0 .or. .not. all(ieee_is_finite(distribution))) error stop 'Tauchen iteration failed'
   residual = maxval(abs(matmul(transpose(probabilities),distribution)-distribution))
   if (minval(distribution) < 0._wp .or. abs(sum(distribution)-1._wp) > 1.e-11_wp &
       .or. residual > 1.e-12_wp) error stop 'Invalid Tauchen stationary distribution'
   mean = dot_product(distribution,nodes)
   variance = dot_product(distribution,(nodes-mean)**2)
   exact_variance = 0.1_wp**2/(1._wp-0.8_wp**2)
   ! Finite-grid/truncated AR(1) approximation: variance need not be exact.
   if (abs(mean) > 1.e-11_wp .or. abs(variance-exact_variance) > 0.05_wp*exact_variance) &
      error stop 'Unexpected AR(1) approximation error'
   print '(a,i0)', 'Tauchen AR(1) states: ', n
   print '(a,es12.4)', 'Mean: ', mean
   print '(a,2f15.10)', 'Discrete and continuous variance: ', variance,exact_variance
   print '(a,es12.4)', 'Equilibrium residual: ', residual
   print *, 'PASS econ-toolchain'
end program main
