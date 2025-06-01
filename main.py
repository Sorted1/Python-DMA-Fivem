import struct
import numpy as np
import memprocfs
import time
import math

def rmatrix(memory, address):
    data = memory.read(address, 64)  # 16 floats * 4 bytes
    values = struct.unpack('16f', data)
    matrix = np.array(values, dtype=np.float32).reshape((4, 4))
    return matrix

def tmatrix(matrix):
    return matrix.T

def world_to_screen(world_pos, memory, base_address, viewport_offset, screen_width, screen_height):
    viewport_ptr_bytes = memory.read(base_address + viewport_offset, 8)
    viewport_ptr = struct.unpack('<Q', viewport_ptr_bytes)[0]

    view_matrix = rmatrix(memory, viewport_ptr + 0x24C)
    view_matrix = tmatrix(view_matrix)

    vec_x = view_matrix[1]
    vec_y = view_matrix[2]
    vec_z = view_matrix[3]

    x = (vec_x[0] * world_pos[0]) + (vec_x[1] * world_pos[1]) + (vec_x[2] * world_pos[2]) + vec_x[3]
    y = (vec_y[0] * world_pos[0]) + (vec_y[1] * world_pos[1]) + (vec_y[2] * world_pos[2]) + vec_y[3]
    z = (vec_z[0] * world_pos[0]) + (vec_z[1] * world_pos[1]) + (vec_z[2] * world_pos[2]) + vec_z[3]

    if z <= 0.1:
        return 0, 0

    inv_z = 1.0 / z
    x *= inv_z
    y *= inv_z

    half_width = screen_width / 2
    half_height = screen_height / 2

    screen_x = x + half_width + (0.5 * x * screen_width + 0.5)
    screen_y = half_height - (0.5 * y * screen_height + 0.5)

    return int(screen_x), int(screen_y)

def localpos(memory, base_address, world_offset, localplayer_offset, pos_offset):
    world_ptr_bytes = memory.read(base_address + world_offset, 8)
    world_ptr = struct.unpack('<Q', world_ptr_bytes)[0]

    localplayer_bytes = memory.read(world_ptr + localplayer_offset, 8)
    localplayer_ptr = struct.unpack('<Q', localplayer_bytes)[0]

    if localplayer_ptr == 0:
        raise Exception("Local player pointer is NULL!")

    pos_bytes = memory.read(localplayer_ptr + pos_offset, 12)
    x, y, z = struct.unpack('fff', pos_bytes)
    return (x, y, z)

def invisable(memory, base_address, world_offset, localplayer_offset, enabled:bool):
    world_ptr_bytes = memory.read(base_address + world_offset, 8)
    world_ptr = struct.unpack('<Q', world_ptr_bytes)[0]

    localplayer_bytes = memory.read(world_ptr + localplayer_offset, 8)
    localplayer_ptr = struct.unpack('<Q', localplayer_bytes)[0]

    if localplayer_ptr == 0:
        raise Exception("Local player pointer is NULL!")

    if enabled:
        value_bytes = struct.pack('<I', 0x1)
        memory.write(localplayer_ptr + 0x2C, value_bytes)
    else:
        value_bytes = struct.pack('<I', 0x37)
        memory.write(localplayer_ptr + 0x2C, value_bytes)

def pedlist(memory, base_address, replay_interface_offset, max_players=256):
    try:
        replay_ptr_bytes = memory.read(base_address + replay_interface_offset, 8)
        if len(replay_ptr_bytes) != 8:
            print(f"Failed to read replay_ptr (got {len(replay_ptr_bytes)} bytes)")
            return
            
        replay_ptr = struct.unpack('<Q', replay_ptr_bytes)[0]
        print(f"Replay Interface Ptr: 0x{replay_ptr:X}")
        
        if replay_ptr == 0:
            print("Replay interface pointer is NULL")
            return
        
        ped_replay_ptr_bytes = memory.read(replay_ptr + 0x18, 8)
        if len(ped_replay_ptr_bytes) != 8:
            print(f"Failed to read ped_replay_ptr (got {len(ped_replay_ptr_bytes)} bytes)")
            return
            
        ped_replay_ptr = struct.unpack('<Q', ped_replay_ptr_bytes)[0]
        print(f"Ped Replay Interface Ptr: 0x{ped_replay_ptr:X}")
        
        if ped_replay_ptr == 0:
            print("Ped replay interface pointer is NULL")
            return
        
        ped_list_ptr_bytes = memory.read(ped_replay_ptr + 0x100, 8)
        if len(ped_list_ptr_bytes) != 8:
            print(f"Failed to read ped_list_ptr (got {len(ped_list_ptr_bytes)} bytes)")
            return
            
        ped_list_ptr = struct.unpack('<Q', ped_list_ptr_bytes)[0]
        print(f"Ped List Ptr: 0x{ped_list_ptr:X}")
        
        if ped_list_ptr == 0:
            print("Ped list pointer is NULL")
            return
        
        print("\nListing all peds:")
        for i in range(max_players):
            try:
                ped_ptr_bytes = memory.read(ped_list_ptr + (i * 0x10), 8)
                if len(ped_ptr_bytes) != 8:
                    continue
                    
                ped_ptr = struct.unpack('<Q', ped_ptr_bytes)[0]
                
                if ped_ptr != 0:
                    print(f"Ped {i}: 0x{ped_ptr:X}")
                    
            except Exception as e:
                print(f"Error reading ped {i}: {str(e)}")
                continue
    
    except Exception as e:
        print(f"Error in print_all_peds: {str(e)}")

if __name__ == "__main__":
    vmm = memprocfs.Vmm(['-device', 'fpga'])
    proc = vmm.process('FiveM_GTAProcess.exe')
    base = proc.module('FiveM_GTAProcess.exe').base
    memory = proc.memory

    # Offsets (update if needed)
    viewport_offset = 0x201DBA0
    world_offset = 0x25B14B0
    localplayer_offset = 0x8
    pos_offset = 0x90
    replay_interface_offset = 0x1FBD4F0

    # Screen resolution
    screen_w, screen_h = 2560, 1440
  
    world_ptr_bytes = memory.read(base + world_offset, 8)
    world_ptr = struct.unpack('<Q', world_ptr_bytes)[0]
    localplayer_bytes = memory.read(world_ptr + localplayer_offset, 8)
    localplayer_ptr = struct.unpack('<Q', localplayer_bytes)[0]

    print("Invisible toggle")
    while True:
        choice = input("Inv: yes or no: ")
        if choice == "yes":
            invisable(memory, base, world_offset, localplayer_offset, True)
        else:
            invisable(memory, base, world_offset, localplayer_offset, False)
        pedlist(memory, base, replay_interface_offset)
