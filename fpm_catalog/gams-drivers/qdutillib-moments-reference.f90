! Independent API consumer; MIT: licenses/moments-nufft2d-drivers-MIT.txt.
program main
   use QDUtil_NumParameters_m,only:Rkind
   use QDUtil_Quadrature_m,only:Quadrature_t,Init_Quadrature,dealloc_Quadrature
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   integer,parameter::orders(*)=[1,2,3,4,6,8,12]
   type(Quadrature_t)::q
   real(Rkind),allocatable::nodes(:),weights(:),terms(:)
   real(Rkind)::value,reference,scale,error,worst,pi,tmp,even_moment
   integer::family,order_id,n,p,i,j,status,rules,moments,shifted
   pi=acos(-1.0_Rkind); worst=0; rules=0; moments=0; shifted=0
   do family=1,2
      do order_id=1,size(orders)
         n=orders(order_id)
         if (family==1) then
            call Init_Quadrature(q,nq=n,name='LegendreP',err=status)
         else
            call Init_Quadrature(q,nq=n,name='HO',err=status)
         end if
         if (status/=0) error stop 'quadrature initialization status'
         if (.not.allocated(q%x).or..not.allocated(q%w)) error stop 'quadrature storage'
         if (any(shape(q%x)/=[1,n]).or.size(q%w)/=n) error stop 'quadrature shape'
         if (.not.all(ieee_is_finite(q%x)).or..not.all(ieee_is_finite(q%w))) error stop 'nonfinite rule'
         if (any(q%w<=0)) error stop 'positive weights'
         allocate(nodes(n),weights(n),terms(n))
         nodes=q%x(1,:); weights=q%w
         ! HO stores full-function weights; recover Gaussian-weighted polynomial moments.
         if (family==2) weights=weights*exp(-nodes**2)
         if (family==1.and.any(abs(nodes)>=1)) error stop 'Legendre interval'
         do i=2,n
            tmp=nodes(i); value=weights(i); j=i-1
            do while(j>=1)
               if (nodes(j)<=tmp) exit
               nodes(j+1)=nodes(j); weights(j+1)=weights(j); j=j-1
            end do
            nodes(j+1)=tmp; weights(j+1)=value
         end do
         if (maxval(abs(nodes+nodes(n:1:-1)))>1e-11_Rkind*max(1.0_Rkind,maxval(abs(nodes)))) &
            error stop 'node symmetry'
         if (maxval(abs(weights-weights(n:1:-1)))>1e-11_Rkind*max(1.0_Rkind,maxval(abs(weights)))) &
            error stop 'weight symmetry'
         even_moment=sqrt(pi)
         do p=0,2*n-1
            reference=0
            if (mod(p,2)==0) then
               if (family==1) then
                  reference=2.0_Rkind/real(p+1,Rkind)
               else
                  if (p>0) even_moment=even_moment*real(p-1,Rkind)/2
                  reference=even_moment
               end if
            end if
            terms=weights*nodes**p
            call check(sum(terms),reference,sum(abs(terms)))
            moments=moments+1
         end do
         if (family==1) then
            do p=0,min(2*n-1,8)
               terms=weights*(nodes+2)**p
               reference=(3.0_Rkind**(p+1)-1)/real(p+1,Rkind)
               call check(sum(terms),reference,sum(abs(terms)))
               shifted=shifted+1
            end do
         end if
         call dealloc_Quadrature(q)
         if (allocated(q%x).or.allocated(q%w)) error stop 'quadrature deallocation'
         deallocate(nodes,weights,terms)
         rules=rules+1
      end do
   end do
   if (rules/=14.or.moments/=144.or.shifted/=47) error stop 'fixture accounting'
   print '(a,i0,a,i0,a,i0)', 'Rules: ',rules,'; Legendre/Gaussian moments: ',moments,'; shifted moments: ',shifted
   print '(a)', 'Orders 1,2,3,4,6,8,12: positive weights, symmetry, exact polynomial moments and deallocation.'
   print '(a,es12.4)', 'Maximum moment error normalized by reference/absolute contributions: ',worst
   print '(a)', 'PASS qdutillib-moments-reference'
contains
   subroutine check(actual,expected,contributions)
      real(Rkind),intent(in)::actual,expected,contributions
      if (.not.ieee_is_finite(actual)) error stop 'nonfinite moment'
      scale=max(1.0_Rkind,abs(expected),contributions)
      error=abs(actual-expected)/scale
      if (error>5e-11_Rkind) error stop 'analytical polynomial moment'
      worst=max(worst,error)
   end subroutine check
end program main
