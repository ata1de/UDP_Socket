# Texto de exemplo
texto = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum vehicula ex nibh, id pharetra lorem elementum at. Maecenas accumsan, libero et tristique convallis, velit erat facilisis purus, quis ullamcorper risus elit vitae dui. Donec id nunc sit amet sapien consequat vestibulum. Ut condimentum velit ut risus posuere, ut dapibus ex dictum. Curabitur nec vehicula orci. Duis tincidunt felis sed malesuada faucibus. Curabitur consectetur nisl ut cursus dapibus. Curabitur id orci sit amet nunc egestas sodales. Etiam sodales semper lectus, eget dignissim purus porttitor sit amet. Sed fermentum, turpis nec convallis accumsan, lorem est tincidunt lectus, at vulputate tortor tortor at augue. Cras ac dui nec lacus tincidunt eleifend ut sit amet magna. Fusce at ligula ut nunc dictum tincidunt. Vivamus feugiat libero eget nulla lacinia, at vehicula magna volutpat. Vivamus sit amet purus ut ex lacinia vehicula vel non eros. Aenean congue lectus vel nisi sodales laoreet. Integer aliquet ligula in orci dapibus mollis. Sed elementum nisi vitae risus eleifend, ut tempor odio pretium. Integer venenatis urna at urna ullamcorper volutpat. Nam convallis, mi sit amet varius venenatis, turpis ligula iaculis erat, a aliquet nisi eros a dui. Praesent ac eros nec magna auctor ultricies. Nunc hendrerit elit non metus tincidunt, quis scelerisque nunc efficitur. Sed facilisis purus a varius sagittis. Curabitur nec magna at augue feugiat gravida. Aliquam erat volutpat. Nullam luctus orci ut nisi condimentum, sit amet hendrerit nulla malesuada. Mauris scelerisque interdum metus. Ut consectetur, ligula vel vestibulum interdum,"

# Converter o texto para bytes
bytes_texto = texto.encode('utf-8')

# Obter a quantidade de bytes
quantidade_bytes = len(bytes_texto)

# Exibir a quantidade de bytes
print(f"O texto tem {quantidade_bytes} bytes.")
