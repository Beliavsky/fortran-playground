! Independent API consumer; MIT: licenses/lapack-spectra-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use linear_algebra, only: eigh,la_state
   implicit none
   integer,parameter::sizes(*)=[1,2,3,5]
   real(real64),parameter::scales(*)=[-4.0_real64,0.5_real64,2.0_real64]
   real(real64),allocatable::a(:,:),input(:,:),saved(:,:),q(:,:),v(:,:),w(:),expected(:),d(:)
   real(real64)::bad(2,3),bad_w(2),normalization,t,value,residual,orthogonal,worst_w,worst_r,worst_o
   type(la_state)::state
   integer::in,n,pattern,is,rotation,triangle,mode,i,j,k,calls,fixtures
   bad=0
   call eigh(bad,bad_w,err=state)
   if (.not.state%error()) error stop 'nonsquare input guard'
   calls=0; fixtures=0; worst_w=0; worst_r=0; worst_o=0
   do in=1,size(sizes)
      n=sizes(in)
      allocate(a(n,n),input(n,n),saved(n,n),q(n,n),v(n,n),w(n),expected(n),d(n))
      do pattern=1,4
         do is=1,size(scales)
            do i=1,n
               select case(pattern)
               case(1)
                  d(i)=real(2*i-n-1,real64)
               case(2)
                  d(i)=2
               case(3)
                  d(i)=real(i-1,real64)
               case(4)
                  d(i)=0
               end select
            end do
            d=d*scales(is); expected=d
            call sort(expected)
            normalization=max(1.0_real64,maxval(abs(d)))
            do rotation=1,2
               q=0
               do i=1,n
                  q(i,i)=1
               end do
               if (rotation==2) then
                  t=real(sum([(i*i,i=1,n)]),real64)
                  do j=1,n
                     do i=1,n
                        q(i,j)=q(i,j)-2*real(i*j,real64)/t
                     end do
                  end do
               end if
               a=0
               do j=1,n
                  do i=1,n
                     do k=1,n
                        a(i,j)=a(i,j)+q(i,k)*d(k)*q(j,k)
                     end do
                  end do
               end do
               fixtures=fixtures+1
               do triangle=1,2
                  input=a
                  ! Finite poison in the unused half checks the triangle selector.
                  do j=1,n
                     do i=1,n
                        if ((triangle==1.and.i<j).or.(triangle==2.and.i>j)) &
                           input(i,j)=real(1000+17*i+31*j,real64)
                     end do
                  end do
                  saved=input
                  do mode=1,2
                     if (mode==1) then
                        call eigh(input,w,upper_a=triangle==2,err=state)
                     else
                        call eigh(input,w,v,upper_a=triangle==2,err=state)
                     end if
                     if (state%error()) error stop 'eigh returned error'
                     if (any(input/=saved)) error stop 'default input preservation'
                     if (.not.all(ieee_is_finite(w))) error stop 'nonfinite eigenvalues'
                     value=maxval(abs(w-expected))/normalization
                     worst_w=max(worst_w,value)
                     if (value>2e-12_real64) error stop 'known eigenvalues'
                     if (mode==2) then
                        if (.not.all(ieee_is_finite(v))) error stop 'nonfinite eigenvectors'
                        residual=0; orthogonal=0
                        do j=1,n
                           do i=1,n
                              value=0
                              do k=1,n
                                 value=value+a(i,k)*v(k,j)
                              end do
                              residual=max(residual,abs(value-w(j)*v(i,j))/normalization)
                              value=0
                              do k=1,n
                                 value=value+v(k,i)*v(k,j)
                              end do
                              if (i==j) value=value-1
                              orthogonal=max(orthogonal,abs(value))
                           end do
                        end do
                        if (residual>5e-12_real64.or.orthogonal>5e-12_real64) &
                           error stop 'eigenvector residual/orthogonality'
                        worst_r=max(worst_r,residual); worst_o=max(worst_o,orthogonal)
                     end if
                     calls=calls+1
                  end do
               end do
            end do
         end do
      end do
      deallocate(a,input,saved,q,v,w,expected,d)
   end do
   if (fixtures/=96.or.calls/=384) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Known-spectrum symmetric matrices: ',fixtures,'; eigh calls: ',calls
   print '(a)', 'Both triangle selectors with unused-half poison; eigenvalues only and eigenvectors.'
   print '(a,es12.4)', 'Maximum normalized eigenvalue error: ',worst_w
   print '(a,es12.4)', 'Maximum normalized scalar eigenvector residual: ',worst_r
   print '(a,es12.4)', 'Maximum scalar orthogonality error: ',worst_o
   print '(a)', 'PASS lapack-eigen-reference'
contains
   subroutine sort(x)
      real(real64),intent(inout)::x(:)
      real(real64)::tmp
      integer::i,j
      do i=2,size(x)
         tmp=x(i); j=i-1
         do while(j>=1)
            if (x(j)<=tmp) exit
            x(j+1)=x(j); j=j-1
         end do
         x(j+1)=tmp
      end do
   end subroutine sort
end program main
