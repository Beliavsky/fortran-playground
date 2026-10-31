! Independent API consumer; MIT: licenses/qr-autodiff-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64,int32
   use ieee_arithmetic, only: ieee_is_finite
   use linalg, only: qr_factor
   implicit none
   integer,parameter::rows(*)=[1,2,4,6],cols(*)=[1,2,3,5]
   real(real64),parameter::scales(*)=[-4.0_real64,0.5_real64,2.0_real64]
   real(real64),allocatable::a(:,:),original(:,:),q(:,:),r(:,:),p(:,:)
   integer(int32),allocatable::pivot(:)
   real(real64)::value,expected,scale,reconstruction,orthogonal,lower,worst_r,worst_o
   integer::im,jn,pattern,is,mode,m,n,i,j,k,calls,fixtures
   calls=0; fixtures=0; worst_r=0; worst_o=0
   do im=1,size(rows)
      m=rows(im)
      do jn=1,size(cols)
         n=cols(jn)
         allocate(a(m,n),original(m,n),pivot(n))
         do pattern=1,4
            do is=1,size(scales)
               do j=1,n
                  do i=1,m
                     a(i,j)=real(modulo(7*i+11*j+3*i*j,19)-9,real64)/4
                     if (i==j) a(i,j)=a(i,j)+3
                  end do
               end do
               if (pattern==2.and.n>1) a(:,n)=a(:,1)
               if (pattern==3) a(:,1)=0
               if (pattern==4) a=0
               a=a*scales(is); original=a
               scale=max(1.0_real64,maxval(abs(a)))
               fixtures=fixtures+1
               do mode=1,3
                  if (mode==1) then
                     call qr_factor(a,q=q,r=r)
                     pivot=[(i,i=1,n)]
                  else
                     pivot=0
                     if (mode==3) pivot(1)=1
                     call qr_factor(a,pivot,q=q,r=r,p=p)
                     if (any(pivot<1).or.any(pivot>n)) error stop 'pivot range'
                     do j=1,n
                        if (count(pivot==j)/=1) error stop 'pivot permutation'
                     end do
                     if (mode==3.and.pivot(1)/=1) error stop 'locked column'
                     if (.not.all(ieee_is_finite(p))) error stop 'nonfinite permutation'
                     do j=1,n
                        do i=1,n
                           expected=0
                           if (i==pivot(j)) expected=1
                           if (p(i,j)/=expected) error stop 'permutation matrix'
                        end do
                     end do
                  end if
                  if (any(a/=original)) error stop 'input changed'
                  if (any(shape(q)/=[m,m]).or.any(shape(r)/=[m,n])) error stop 'factor shapes'
                  if (.not.all(ieee_is_finite(q)).or..not.all(ieee_is_finite(r))) error stop 'nonfinite factor'
                  reconstruction=0; orthogonal=0; lower=0
                  do j=1,n
                     do i=1,m
                        value=0
                        do k=1,m
                           value=value+q(i,k)*r(k,j)
                        end do
                        reconstruction=max(reconstruction,abs(value-a(i,pivot(j)))/scale)
                        if (i>j) lower=max(lower,abs(r(i,j))/scale)
                     end do
                  end do
                  do j=1,m
                     do i=1,m
                        value=0
                        do k=1,m
                           value=value+q(k,i)*q(k,j)
                        end do
                        if (i==j) value=value-1
                        orthogonal=max(orthogonal,abs(value))
                     end do
                  end do
                  if (reconstruction>2e-12_real64) error stop 'A P = Q R'
                  if (orthogonal>5e-12_real64) error stop 'Q orthogonality'
                  if (lower>1e-12_real64) error stop 'upper trapezoidal R'
                  worst_r=max(worst_r,reconstruction); worst_o=max(worst_o,orthogonal)
                  calls=calls+1
               end do
            end do
         end do
         deallocate(a,original,pivot)
      end do
   end do
   if (fixtures/=192.or.calls/=576) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Real matrix fixtures: ',fixtures,'; QR factorizations: ',calls
   print '(a)', 'Square/tall/wide, repeated/zero columns, zero matrices; free and locked pivots.'
   print '(a,es12.4)', 'Maximum normalized scalar reconstruction error: ',worst_r
   print '(a,es12.4)', 'Maximum scalar orthogonality error: ',worst_o
   print '(a)', 'PASS linalg-qr-reference'
end program main
