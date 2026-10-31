! Independent API consumer; MIT: licenses/ranking-magic-drivers-MIT.txt.
program main
   use iso_fortran_env,only:int64,real64
   use ieee_arithmetic,only:ieee_is_finite
   use M_LA,only:mat_magic
   implicit none
   real(real64),allocatable::a(:,:)
   integer(int64),allocatable::entries(:,:)
   integer(int64)::target,total,diagonal,reverse_diagonal
   integer::n,rows,padding,repeat,i,j,k,calls,value_checks,sum_checks,classes(3)
   calls=0; value_checks=0; sum_checks=0; classes=0
   do n=1,32
      if (n==2) cycle ! No normal order-two magic square exists.
      if (mod(n,2)==1) then
         classes(1)=classes(1)+1
      else if (mod(n,4)==0) then
         classes(2)=classes(2)+1
      else
         classes(3)=classes(3)+1
      end if
      target=int(n,int64)*(int(n,int64)**2+1)/2
      do padding=0,3,3
         rows=n+padding
         allocate(a(rows,n),entries(n,n))
         do repeat=1,2
            a=-9999
            call mat_magic(a,rows,n)
            if (.not.all(ieee_is_finite(a))) error stop 'nonfinite matrix'
            if (padding>0) then
               if (any(a(n+1:,:)/=-9999)) error stop 'leading dimension padding overwritten'
            end if
            entries=nint(a(:n,:),kind=int64)
            if (any(a(:n,:)/=real(entries,real64))) error stop 'noninteger magic entries'
            if (any(entries<1).or.any(entries>int(n,int64)**2)) error stop 'entry range'
            do k=1,n*n
               if (count(entries==k)/=1) error stop 'entries not a permutation'
            end do
            value_checks=value_checks+n*n
            diagonal=0; reverse_diagonal=0
            do i=1,n
               total=0
               do j=1,n
                  total=total+entries(i,j)
               end do
               if (total/=target) error stop 'row sum'
               total=0
               do j=1,n
                  total=total+entries(j,i)
               end do
               if (total/=target) error stop 'column sum'
               diagonal=diagonal+entries(i,i)
               reverse_diagonal=reverse_diagonal+entries(i,n+1-i)
            end do
            if (diagonal/=target.or.reverse_diagonal/=target) error stop 'diagonal sums'
            sum_checks=sum_checks+2*n+2
            calls=calls+1
         end do
         deallocate(a,entries)
      end do
   end do
   if (calls/=124.or.value_checks/=45744.or.sum_checks/=4456) error stop 'accounting'
   if (any(classes/=[16,8,7])) error stop 'order families'
   print '(a,i0)', 'Magic-square calls: ',calls
   print '(a,i0,a,i0)', 'Entry checks: ',value_checks,'; exact line-sum checks: ',sum_checks
   print '(a)', 'Orders 1 and 3..32; odd/doubly-even/singly-even; compact/padded storage; repeated calls.'
   print '(a)', 'PASS m-la-magic-reference'
end program
