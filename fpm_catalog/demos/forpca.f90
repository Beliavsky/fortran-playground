program main
   use forpca, only: tpca
   use kinds, only: rk
   implicit none
   type(tpca) :: analysis
   real(rk) :: data(5,2)
   real(rk), allocatable :: coefficients(:,:), variances(:), scores(:), reconstructed(:,:)
   real(rk) :: centered(5,2), expected_direction(2)
   data(:,1) = [-2.0_rk,-1.0_rk,0.0_rk,1.0_rk,2.0_rk]
   data(:,2) = 2*data(:,1)+3
   ! This API returns the full basis. Use its leading direction for a rank-one projection.
   call analysis%pca(data,1,'svd',coefficients,latent=variances)
   expected_direction = [1.0_rk,2.0_rk]/sqrt(5.0_rk)
   if (abs(abs(dot_product(coefficients(:,1),expected_direction))-1.0_rk) > 1.e-8_rk) &
      error stop 'incorrect principal direction'
   centered = data
   centered(:,2) = centered(:,2)-3
   scores = matmul(centered,coefficients(:,1))
   allocate(reconstructed(5,2))
   reconstructed(:,1) = scores*coefficients(1,1)
   reconstructed(:,2) = scores*coefficients(2,1)+3
   if (maxval(abs(reconstructed-data)) > 1.e-8_rk) error stop 'incorrect rank-one reconstruction'
   print *, 'Principal direction:', coefficients(:,1)
   print *, 'Maximum rank-one reconstruction error:', maxval(abs(reconstructed-data))
   call analysis%finalize()
   print *, 'PASS forpca'
end program main
