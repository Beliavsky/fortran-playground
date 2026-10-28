program demo_sodium
   use sodium
   implicit none
   character(len=SODIUM_crypto_secretbox_KEYBYTES) :: key
   character(len=SODIUM_crypto_secretbox_NONCEBYTES) :: nonce
   character(len=*), parameter :: message='A message from the Fortran playground'
   character(len=len(message)+SODIUM_crypto_secretbox_MACBYTES) :: cipher
   character(len=len(message)) :: recovered
   integer :: status

   status = sodium_init()
   if (status < 0) error stop 'Could not initialize libsodium'
   call crypto_secretbox_keygen(key)
   call randombytes_buf(nonce)
   status = crypto_secretbox_easy(cipher,message,nonce,key)
   if (status /= 0) error stop 'Encryption failed'
   status = crypto_secretbox_open_easy(recovered,cipher,nonce,key)
   if (status /= 0) error stop 'Authentication/decryption failed'
   if (recovered /= message) error stop 'Round trip changed the message'
   print '(a)', 'Original:  '//message
   print '(a)', 'Recovered: '//recovered
   print '(a,i0)', 'Ciphertext bytes (including authentication tag): ',len(cipher)
   ! Corruption must be detected, not silently decrypted.
   cipher(1:1) = achar(ieor(iachar(cipher(1:1)),1))
   status = crypto_secretbox_open_easy(recovered,cipher,nonce,key)
   if (status == 0) error stop 'Tampered ciphertext was accepted'
   print '(a)', 'Tampered ciphertext rejected.'
   print '(a)', 'PASS sodium'
end program
