! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats, only: pca, pca_transform, pca_inverse_transform
   use stdlib_linalg_state, only: linalg_state_type
   implicit none
   real(real64) :: x(6,3),saved(6,3),q(3,3),axes(3,3),s(3),mu(3),offset(3),amplitude(3)
   real(real64) :: scores(6,3),restored(6,3),expected(6,3),expected_scores(6,3),eye(3,3),sgn,loss
   type(linalg_state_type) :: err
   character(3),parameter :: methods(2)=['svd','cov']
   integer :: t,m,i,j,r,fits,projections
   q=reshape([-1._real64,2._real64,2._real64,2._real64,-1._real64,2._real64, &
              2._real64,2._real64,-1._real64],[3,3])/3
   eye=0
   do i=1,3
      eye(i,i)=1
   end do
   fits=0; projections=0
   do t=1,24
      amplitude=[3._real64+t/16._real64,2._real64+t/32._real64,1._real64+t/64._real64]
      offset=[t/4._real64,-t/8._real64,0.5_real64]
      do j=1,3
         saved(2*j-1,:)=offset+amplitude(j)*q(j,:)
         saved(2*j,:)=offset-amplitude(j)*q(j,:)
      end do
      do m=1,2
         x=saved
         call pca(x,axes,s,x_mean=mu,method=methods(m),err=err)
         if(.not.err%ok()) error stop 'PCA status'
         if(.not.all(ieee_is_finite(axes)).or..not.all(ieee_is_finite(s)).or. &
            .not.all(ieee_is_finite(mu))) error stop 'Nonfinite PCA result'
         if(any(x/=saved)) error stop 'PCA input preservation'
         if(maxval(abs(mu-offset))>2.e-11_real64) error stop 'Known column means'
         if(maxval(abs(s-sqrt(2._real64)*amplitude))>2.e-11_real64) error stop 'Known singular values'
         if(maxval(abs(s*s/5-2*amplitude**2/5))>2.e-11_real64) error stop 'Known covariance variances'
         if(maxval(abs(matmul(axes,transpose(axes))-eye))>2.e-11_real64) error stop 'Orthonormal PCA axes'
         do j=1,3
            if(abs(abs(dot_product(axes(j,:),q(j,:)))-1)>2.e-11_real64) error stop 'Known principal direction'
         end do
         fits=fits+1
         do r=1,3
            expected_scores=0
            expected=spread(offset,1,6)
            do j=1,r
               sgn=sign(1._real64,dot_product(axes(j,:),q(j,:)))
               expected_scores(2*j-1,j)=sgn*amplitude(j)
               expected_scores(2*j,j)=-sgn*amplitude(j)
               expected(2*j-1,:)=offset+amplitude(j)*q(j,:)
               expected(2*j,:)=offset-amplitude(j)*q(j,:)
            end do
            call pca_transform(saved,axes(:r,:),scores(:,:r),mu)
            call pca_inverse_transform(scores(:,:r),axes(:r,:),restored,mu)
            if(.not.all(ieee_is_finite(scores(:,:r))).or..not.all(ieee_is_finite(restored))) &
               error stop 'Nonfinite PCA projection'
            if(maxval(abs(scores(:,:r)-expected_scores(:,:r)))>2.e-11_real64) error stop 'Known PCA scores'
            if(maxval(abs(restored-expected))>2.e-11_real64) error stop 'Known retained-component projection'
            loss=sum((saved-restored)**2)
            if(abs(loss-2*sum(amplitude(r+1:)**2))>2.e-11_real64) error stop 'Known discarded variance'
            projections=projections+1
         end do
      end do
   end do
   print '(a,i0,a,i0)', 'Analytic rotated PCA: fits=',fits,', projections and inverse projections=',projections
   print '(a)', 'PASS stdlib-pca-reference'
end program
