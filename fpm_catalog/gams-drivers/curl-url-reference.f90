! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
! Offline parsing only: no request is made.
program main
   use iso_c_binding, only: c_ptr,c_associated,c_null_ptr
   use curl
   implicit none
   type(c_ptr) :: handle
   character(40) :: host,port,path,query,newpath
   character(:),allocatable :: url,part
   integer :: n
   do n=1,64
      write(host,'(a,i0,a)') 'node',n,'.example.org'
      write(port,'(i0)') 8000+n
      write(path,'(a,i0,a)') '/data/',n,'/input.csv'
      write(query,'(a,i0)') 'sample=',3*n
      write(newpath,'(a,i0,a)') '/output/',n,'.dat'
      url='https://'//trim(host)//':'//trim(port)//trim(path)//'?'//trim(query)
      handle=curl_url()
      if(.not.c_associated(handle)) error stop 'URL handle'
      call check(curl_url_set(handle,CURLUPART_URL,url))
      call check(curl_url_get(handle,CURLUPART_HOST,part))
      if(part/=trim(host)) error stop 'Host'
      call check(curl_url_get(handle,CURLUPART_PORT,part))
      if(part/=trim(port)) error stop 'Port'
      call check(curl_url_get(handle,CURLUPART_PATH,part))
      if(part/=trim(path)) error stop 'Path'
      call check(curl_url_get(handle,CURLUPART_QUERY,part))
      if(part/=trim(query)) error stop 'Query'
      call check(curl_url_set(handle,CURLUPART_PATH,trim(newpath)))
      call check(curl_url_get(handle,CURLUPART_URL,part))
      url='https://'//trim(host)//':'//trim(port)//trim(newpath)//'?'//trim(query)
      if(part/=url) error stop 'Reconstructed URL'
      call curl_url_cleanup(handle)
      handle=c_null_ptr
   end do
   print '(a)', '64 offline URLs; 320 exact component/reconstruction references'
   print '(a)', 'PASS curl-url-reference'
contains
   subroutine check(rc)
      integer,intent(in) :: rc
      if(rc/=CURLUE_OK) error stop 'libcurl URL API'
   end subroutine
end program
