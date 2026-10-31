! Independent API consumer; MIT: licenses/spectral-wrappers-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use forsvd, only: svd
   implicit none
   integer,parameter::shapes(2,6)=reshape([1,1,2,3,3,2,3,3,4,2,2,5],[2,6])
   real(real64),parameter::scales(*)=[-4.0_real64,0.5_real64,2.0_real64]
   real(real64),allocatable::a(:,:),input(:,:),left(:,:),right(:,:),u(:,:),vt(:,:),s(:),expected(:),d(:)
   real(real64)::value,normalization,reconstruction,orthogonal,worst_s,worst_r,worst_o,triplet,worst_t,lambda
   integer::shape_id,m,n,k,pattern,is,rotation,mode,i,j,l,b,c,cols_u,rows_v,calls,fixtures
   calls=0; fixtures=0; worst_s=0; worst_r=0; worst_o=0; worst_t=0
   do shape_id=1,size(shapes,2)
      m=shapes(1,shape_id); n=shapes(2,shape_id); k=min(m,n)
      allocate(a(m,n),input(m,n),left(m,m),right(n,n),expected(k),d(k))
      do pattern=1,4
         do is=1,size(scales)
            do i=1,k
               select case(pattern)
               case(1)
                  d(i)=real(k-i+1,real64)
               case(2)
                  d(i)=2
               case(3)
                  d(i)=0
                  if (i==1) d(i)=3
               case(4)
                  d(i)=0
               end select
            end do
            expected=d*abs(scales(is))
            d=d*scales(is)
            normalization=max(1.0_real64,maxval(abs(d)))
            do rotation=1,2
               call orthogonal_factor(left,rotation)
               call orthogonal_factor(right,rotation)
               a=0
               do j=1,n
                  do i=1,m
                     do l=1,k
                        a(i,j)=a(i,j)+left(i,l)*d(l)*right(j,l)
                     end do
                  end do
               end do
               fixtures=fixtures+1
               do mode=1,3
                  input=a
                  allocate(u(m,m),vt(n,n),s(k))
                  ! Only the first k columns/rows are returned in reduced mode.
                  u=0; vt=0; s=0
                  select case(mode)
                  case(1)
                     call svd(input,u,s,vt)
                  case(2)
                     call svd(input,u,s,vt,method='gesvd')
                  case(3)
                     call svd(input,u,s,vt,method='gesdd')
                  end select
                  if (.not.all(ieee_is_finite(s))) error stop 'nonfinite singular values'
                  if (.not.all(ieee_is_finite(u(:,1:k)))) error stop 'nonfinite U'
                  if (.not.all(ieee_is_finite(vt(1:k,:)))) error stop 'nonfinite VT'
                  cols_u=k; rows_v=k
                  value=maxval(abs(s-expected))/normalization
                  if (value>2e-12_real64) error stop 'known singular values'
                  worst_s=max(worst_s,value)
                  if (any(s<0)) error stop 'negative singular value'
                  do i=2,k
                     if (s(i)>s(i-1)) error stop 'singular value ordering'
                  end do
                  reconstruction=0; orthogonal=0
                  do j=1,n
                     do i=1,m
                        value=0
                        do l=1,k
                           value=value+u(i,l)*s(l)*vt(l,j)
                        end do
                        reconstruction=max(reconstruction,abs(value-a(i,j))/normalization)
                     end do
                  end do
                  do j=1,cols_u
                     do i=1,cols_u
                        value=0
                        do l=1,m
                           value=value+u(l,i)*u(l,j)
                        end do
                        if (i==j) value=value-1
                        orthogonal=max(orthogonal,abs(value))
                     end do
                  end do
                  do j=1,rows_v
                     do i=1,rows_v
                        value=0
                        do l=1,n
                           value=value+vt(i,l)*vt(j,l)
                        end do
                        if (i==j) value=value-1
                        orthogonal=max(orthogonal,abs(value))
                     end do
                  end do
                  ! Independently check returned reduced singular-vector eigenspaces.
                  triplet=0
                  do j=1,cols_u
                     lambda=0
                     if (j<=k) lambda=s(j)**2
                     do i=1,m
                        value=0
                        do b=1,n
                           do c=1,m
                              value=value+a(i,b)*a(c,b)*u(c,j)
                           end do
                        end do
                        triplet=max(triplet,abs(value-lambda*u(i,j))/normalization**2)
                     end do
                  end do
                  do j=1,rows_v
                     lambda=0
                     if (j<=k) lambda=s(j)**2
                     do i=1,n
                        value=0
                        do b=1,m
                           do c=1,n
                              value=value+a(b,i)*a(b,c)*vt(j,c)
                           end do
                        end do
                        triplet=max(triplet,abs(value-lambda*vt(j,i))/normalization**2)
                     end do
                  end do
                  if (triplet>1e-11_real64) error stop 'singular-vector eigenspace residual'
                  worst_t=max(worst_t,triplet)
                  if (reconstruction>5e-12_real64.or.orthogonal>5e-12_real64) &
                     error stop 'SVD reconstruction/orthogonality'
                  worst_r=max(worst_r,reconstruction); worst_o=max(worst_o,orthogonal)
                  if (allocated(u)) deallocate(u)
                  if (allocated(vt)) deallocate(vt)
                  deallocate(s)
                  calls=calls+1
               end do
            end do
         end do
      end do
      deallocate(a,input,left,right,expected,d)
   end do
   if (fixtures/=144.or.calls/=432) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Known-spectrum rectangular matrices: ',fixtures,'; SVD calls: ',calls
   print '(a)', 'Default/GESVD/GESDD; reduced factors, distinct/repeated/rank-one/zero spectra.'
   print '(a,es12.4)', 'Maximum normalized singular-value error: ',worst_s
   print '(a,es12.4)', 'Maximum normalized scalar reconstruction error: ',worst_r
   print '(a,es12.4)', 'Maximum scalar orthogonality error: ',worst_o
   print '(a,es12.4)', 'Maximum normalized scalar singular-vector residual: ',worst_t
   print '(a)', 'PASS forsvd-spectrum-reference'
contains
   subroutine orthogonal_factor(q,variant)
      real(real64),intent(out)::q(:,:)
      integer,intent(in)::variant
      real(real64)::norm
      integer::i,j,n
      n=size(q,1); q=0
      do i=1,n
         q(i,i)=1
      end do
      if (variant==1) return
      norm=real(sum([(i*i,i=1,n)]),real64)
      do j=1,n
         do i=1,n
            q(i,j)=q(i,j)-2*real(i*j,real64)/norm
         end do
      end do
   end subroutine orthogonal_factor
end program main
