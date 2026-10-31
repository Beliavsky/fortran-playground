! Independent failed-probe candidate; MIT: ../../../fpm_catalog/gams-drivers/licenses/sparse-integral-drivers-MIT.txt.
program covariance_variances
   use forpca, only: tpca
   use kinds, only: rk
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(tpca) :: analysis
   real(rk) :: data(5,2), expected(2)
   real(rk), allocatable :: coefficients(:,:),latent(:),explained(:)
   data(:,1) = 10._rk+2*[-2._rk,-1._rk,0._rk,1._rk,2._rk]
   data(:,2) = -4._rk+[1._rk,-2._rk,2._rk,-2._rk,1._rk]
   ! Centered columns are orthogonal, with unbiased variances 40/4 and 14/4.
   expected = [10._rk,3.5_rk]
   call analysis%pca(data,2,'svd',coefficients,latent=latent,explained=explained)
   print '(a,2f14.6)', 'Expected covariance eigenvalues: ',expected
   print '(a,2f14.6)', 'Returned latent variances:       ',latent
   print '(a,2f14.6)', 'Expected explained percentages:  ',100*expected/sum(expected)
   print '(a,2f14.6)', 'Returned explained percentages:  ',explained
   if (.not. all(ieee_is_finite(latent))) error stop 'nonfinite PCA variances'
   if (maxval(abs(latent-expected)) > 1.e-10_rk) error stop 'known covariance eigenvalues'
   if (maxval(abs(explained-100*expected/sum(expected))) > 1.e-10_rk) error stop 'known explained variance'
   call analysis%finalize()
   print '(a)', 'PASS forpca-covariance-variances'
end program covariance_variances
