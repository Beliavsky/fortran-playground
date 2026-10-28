program main
   use iso_fortran_env, only: real64
   use geompack, only: r8tris2
   implicit none
   real(real64) :: nodes(2,5),a(2),b(2),c(2),area
   integer :: triangles(3,10),neighbors(3,10),ntri,i
   nodes=reshape([-1._real64,-1._real64,1._real64,-1._real64, &
      1._real64,1._real64,-1._real64,1._real64,0._real64,0._real64],[2,5])
   call r8tris2(5,nodes,ntri,triangles,neighbors)
   if (ntri/=4) error stop 'Expected four triangles'
   if (any(triangles(:,:ntri)<1).or.any(triangles(:,:ntri)>5)) error stop
   area=0._real64
   do i=1,ntri
      a=nodes(:,triangles(1,i)); b=nodes(:,triangles(2,i)); c=nodes(:,triangles(3,i))
      area=area+abs((b(1)-a(1))*(c(2)-a(2))-(b(2)-a(2))*(c(1)-a(1)))/2
      print '(a,i2,a,3i3)', 'Triangle ',i,':',triangles(:,i)
   end do
   if (abs(area-4._real64)>1e-12_real64) error stop 'Incorrect total area'
   print '(a,f8.3)', 'Total area of square:',area
   print *, 'PASS geompack'
end program main
