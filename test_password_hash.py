import bcrypt

password = b'cake'

password_test = b'$2y$10$OqLCFuQYW27qeyjboqVwyeuJjE4HA6KG9z3DI1pAmJCKZAcJghVvi'

password1 = b'$2y$10$7.yygZOIDA4.hrpqnUV/J.jv3WGJCb6WF/LDYQYmK5i4OygzU8yVC'
password2 = b'$2y$10$odAk38Nhxo77wgjy4UkFauMxPyhXckpQY.EvQ1hTbtljjSljiI4a2'

hash = bcrypt.hashpw(password, bcrypt.gensalt(12))
print(hash)

if bcrypt.hashpw(password, password1) == password1:
    print("We did it Reddit")
else:
    print("God dammit")
