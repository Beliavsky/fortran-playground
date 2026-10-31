! Independent API consumer; MIT: licenses/moments-nufft2d-drivers-MIT.txt.
program main
   use iso_fortran_env,only:real64
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   integer,parameter::counts(*)=[8,31,64],grids(2,3)=reshape([8,10,9,11,16,18],[2,3])
   real(real64),parameter::pi=acos(-1.0_real64),tolerances(*)=[1e-7_real64,1e-10_real64]
   real(real64),allocatable::x(:),y(:),saved_x(:),saved_y(:)
   complex(real64),allocatable::c(:),saved_c(:),fk(:,:),reference(:,:)
   complex(real64)::value,dc
   real(real64)::eps,error,worst,phase,scale
   integer::count_id,grid_id,nj,ms,mt,pattern,sign,tolerance_id,j,k,l,status,calls,coefficients
   interface
      subroutine nufft2d1f90(nj,xj,yj,cj,iflag,eps,ms,mt,fk,ier)
         import real64
         integer::nj,iflag,ms,mt,ier
         real(real64)::xj(nj),yj(nj),eps
         complex(real64)::cj(nj),fk(-ms/2:(ms-1)/2,-mt/2:(mt-1)/2)
      end subroutine nufft2d1f90
   end interface
   calls=0; coefficients=0; worst=0
   do count_id=1,size(counts)
      nj=counts(count_id)
      allocate(x(nj),y(nj),c(nj),saved_x(nj),saved_y(nj),saved_c(nj))
      do grid_id=1,size(grids,2)
         ms=grids(1,grid_id); mt=grids(2,grid_id)
         allocate(fk(-ms/2:(ms-1)/2,-mt/2:(mt-1)/2),reference(-ms/2:(ms-1)/2,-mt/2:(mt-1)/2))
         do pattern=1,4
            do j=1,nj
               x(j)=pi*sin(0.71_real64*j); y(j)=pi*cos(0.43_real64*j)
               c(j)=cmplx(cos(0.13_real64*j),sin(0.17_real64*j),real64)
               select case(pattern)
               case(2)
                  x(j)=0; y(j)=0
               case(3)
                  x(j)=real(2*modulo(j,2)-1,real64)*(pi-1e-6_real64)
                  y(j)=real(2*modulo(j,3)-2,real64)*pi/4
               case(4)
                  c(j)=0
               end select
            end do
            saved_x=x; saved_y=y; saved_c=c; dc=sum(c)/nj
            do sign=-1,1,2
               ! Independent direct sums use the mathematical input before any library call.
               do l=-mt/2,(mt-1)/2
                  do k=-ms/2,(ms-1)/2
                     value=0
                     do j=1,nj
                        phase=real(sign,real64)*(k*x(j)+l*y(j))
                        value=value+c(j)*cmplx(cos(phase),sin(phase),real64)
                     end do
                     reference(k,l)=value/nj
                  end do
               end do
               do tolerance_id=1,size(tolerances)
                  eps=tolerances(tolerance_id)
                  call nufft2d1f90(nj,x,y,c,sign,eps,ms,mt,fk,status)
                  if (status/=0) error stop 'NUFFT success status'
                  if (.not.all(ieee_is_finite(real(fk,real64))).or. &
                     .not.all(ieee_is_finite(aimag(fk)))) error stop 'nonfinite coefficient'
                  if (any(x/=saved_x).or.any(y/=saved_y).or.any(c/=saved_c)) error stop 'input preservation'
                  scale=max(1.0_real64,maxval(abs(reference)))
                  error=maxval(abs(fk-reference))/scale
                  if (error>50*tolerances(tolerance_id)) then
                     print '(a,6i5,a,es12.4)', 'Points/grid/pattern/sign/tolerance: ',nj,ms,mt,pattern,sign, &
                        tolerance_id,' error ',error
                     error stop 'direct Fourier sum'
                  end if
                  if (abs(fk(0,0)-dc)/scale>50*tolerances(tolerance_id)) error stop 'DC normalization'
                  if (pattern==4.and.any(abs(fk)>0)) error stop 'zero strengths'
                  worst=max(worst,error); calls=calls+1; coefficients=coefficients+ms*mt
               end do
            end do
         end do
         deallocate(fk,reference)
      end do
      deallocate(x,y,c,saved_x,saved_y,saved_c)
   end do
   if (calls/=144.or.coefficients/=22416) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Two-dimensional type-1 NUFFT calls: ',calls,'; direct coefficient comparisons: ',coefficients
   print '(a)', 'Even/odd grids, both signs, two tolerances; scattered, coincident, near-boundary and zero-strength data.'
   print '(a,es12.4)', 'Maximum normalized direct-sum error: ',worst
   print '(a)', 'PASS nufft2d-direct-reference'
end program main
