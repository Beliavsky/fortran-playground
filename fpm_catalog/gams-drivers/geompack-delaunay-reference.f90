! Independent API consumer; MIT: licenses/conversion-triangulation-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use geompack,only:r8tris2
   implicit none
   integer,parameter::sizes(*)=[5,9,13]
   real(wp),parameter::scales(*)=[0.5_wp,2.0_wp,8.0_wp]
   real(wp),parameter::interior(2,9)=reshape([0.0_wp,0.0_wp,-0.7_wp,-0.2_wp,0.2_wp,-0.6_wp, &
      0.65_wp,0.1_wp,-0.1_wp,0.7_wp,-0.45_wp,0.45_wp,0.45_wp,0.55_wp, &
      -0.55_wp,-0.65_wp,0.55_wp,-0.45_wp],[2,9])
   real(wp),allocatable::xy(:,:),saved(:,:)
   integer,allocatable::tri(:,:),neighbor(:,:),edges(:,:)
   logical,allocatable::visited(:,:)
   real(wp)::scale,shift(2),a(2),b(2),c(2),area2,area,det,worst_area,worst_circle,value
   integer::layout,n,is,translation,ordering,nt,t,e,u,v,i,j,k,nb,other,match,boundary_edges
   integer::start_t,start_e,next_t,next_e,link,calls,triangles,circle_checks
   calls=0; triangles=0; circle_checks=0; worst_area=0; worst_circle=0
   do layout=1,size(sizes)
      n=sizes(layout)
      allocate(xy(2,n),saved(2,n),tri(3,2*n),neighbor(3,2*n),edges(n,n),visited(3,2*n))
      do is=1,size(scales)
         scale=scales(is)
         do translation=1,2
            shift=0
            if (translation==2) shift=[-3.0_wp,5.0_wp]
            do ordering=1,2
               xy(:,:4)=reshape([-1.0_wp,-1.0_wp,1.0_wp,-1.0_wp,1.0_wp,1.0_wp,-1.0_wp,1.0_wp],[2,4])
               xy(:,5:)=interior(:,:n-4)
               do i=1,n
                  xy(:,i)=scale*xy(:,i)+shift
               end do
               if (ordering==2) xy=xy(:,n:1:-1)
               saved=xy; nt=0; tri=0; neighbor=0
               call r8tris2(n,xy,nt,tri,neighbor)
               if (nt/=2*n-6) error stop 'Euler triangle count'
               if (.not.all(ieee_is_finite(xy)).or.any(xy/=saved)) error stop 'coordinate restoration'
               if (any(tri(:,:nt)<1).or.any(tri(:,:nt)>n)) error stop 'vertex range'
               do i=1,n
                  if (.not.any(tri(:,:nt)==i)) error stop 'unused vertex'
               end do
               edges=0; area=0; boundary_edges=0; start_t=0; start_e=0
               do t=1,nt
                  do other=1,t-1
                     if (all([(any(tri(:,other)==tri(i,t)),i=1,3)])) error stop 'duplicate triangle'
                  end do
                  a=xy(:,tri(1,t)); b=xy(:,tri(2,t)); c=xy(:,tri(3,t))
                  area2=cross(b-a,c-a)
                  if (area2<=1e-14_wp*scale**2) error stop 'triangle orientation or degeneracy'
                  area=area+area2/2
                  do i=1,n
                     if (any(tri(:,t)==i)) cycle
                     a=xy(:,tri(1,t))-xy(:,i); b=xy(:,tri(2,t))-xy(:,i); c=xy(:,tri(3,t))-xy(:,i)
                     det=sum(a*a)*cross(b,c)-sum(b*b)*cross(a,c)+sum(c*c)*cross(a,b)
                     value=det/max(1.0_wp,scale**4)
                     if (value>1e-10_wp) error stop 'point inside circumcircle'
                     worst_circle=max(worst_circle,value); circle_checks=circle_checks+1
                  end do
                  do e=1,3
                     u=tri(e,t); v=tri(mod(e,3)+1,t)
                     edges(min(u,v),max(u,v))=edges(min(u,v),max(u,v))+1
                     nb=neighbor(e,t)
                     if (nb>0) then
                        if (nb>nt.or.nb==t) error stop 'neighbor range'
                        match=0
                        do k=1,3
                           if (tri(k,nb)==v.and.tri(mod(k,3)+1,nb)==u) then
                              if (neighbor(k,nb)/=t) error stop 'neighbor reciprocity'
                              match=match+1
                           end if
                        end do
                        if (match/=1) error stop 'neighbor shared edge'
                     else if (nb<0) then
                        boundary_edges=boundary_edges+1; start_t=t; start_e=e
                     else
                        error stop 'missing neighbor'
                     end if
                  end do
               end do
               if (any(edges>2).or.count(edges==1)/=4.or.count(edges>0)/=3*n-7) error stop 'edge incidence'
               if (boundary_edges/=4) error stop 'boundary count'
               visited=.false.; t=start_t; e=start_e
               do j=1,4
                  if (visited(e,t).or.neighbor(e,t)>=0) error stop 'boundary cycle'
                  visited(e,t)=.true.; link=-neighbor(e,t)
                  next_t=link/3; next_e=mod(link,3)+1
                  if (next_t<1.or.next_t>nt) error stop 'boundary link range'
                  t=next_t; e=next_e
               end do
               if (t/=start_t.or.e/=start_e) error stop 'boundary cycle closure'
               value=abs(area-4*scale**2)/max(1.0_wp,4*scale**2)
               if (value>5e-12_wp) error stop 'known rectangle area'
               worst_area=max(worst_area,value); triangles=triangles+nt; calls=calls+1
            end do
         end do
      end do
      deallocate(xy,saved,tri,neighbor,edges,visited)
   end do
   if (calls/=36.or.triangles/=432.or.circle_checks/=3360) error stop 'accounting'
   print '(a,i0,a,i0)', 'Planar triangulations: ',calls,'; checked triangles: ',triangles
   print '(a,i0)', 'Independent empty-circumcircle tests: ',circle_checks
   print '(a)', 'Known hull/area; all vertices; edge incidence; reciprocal neighbors; boundary cycle; restored coordinates.'
   print '(a,es12.4)', 'Maximum normalized area error: ',worst_area
   print '(a,es12.4)', 'Maximum positive normalized incircle determinant: ',worst_circle
   print '(a)', 'PASS geompack-delaunay-reference'
contains
   pure function cross(a,b) result(value)
      real(wp),intent(in)::a(2),b(2)
      real(wp)::value
      value=a(1)*b(2)-a(2)*b(1)
   end function
end program
