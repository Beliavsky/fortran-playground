# FED width policy reference correction

Pinned revision: `d735aa2b3bd6b20840bcc16ff569e8cfc0492267`. Source SHA256 (UTF-8 LF): `27787082ee83d9a4089c470fd4d68a4f032aa21e46609c5bc09b453c0bcbf227`.

The consumer assumed native Fw.d at the requested width. FED deliberately raises width to at least d+2. This failed expectation is corrected in the final reference; it is not an upstream numerical defect.
