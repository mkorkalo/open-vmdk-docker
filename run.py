#!/usr/bin/python3

import argparse
from pathlib import Path
import subprocess

DOCKER_TAG_NAME = "openvmdk"
DOCKER_OVF_DIR = "/out/ovf_dir"
DOCKER_OVA_OUTPUTDIR = "/out/ova_outputdir"
DOCKER_VMDK_IMAGE_DIR = "/out/vmdk_image_dir"

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("-q", "--no-qemu-convert", action="store_true", default=False)
parser.add_argument("-Q", "--qemu-convert-options", type=str, default="adapter_type=lsilogic,subformat=streamOptimized,compat6")
parser.add_argument("--ova_name", "-n", type=str, default="my-vm")
parser.add_argument(
    "--ovf_template", "-t", type=str, default="./template-hw14-bios.ovf"
)
parser.add_argument("--ova_outputdir", "-o", type=str, default=".")
parser.add_argument("--vmdk_image", "-i", nargs="+", type=str, required=True)
args = parser.parse_args()

qconv = not args.no_qemu_convert
print(f"qemu convert: {not args.no_qemu_convert}")
if qconv:
    print(f"qemu convert options: {args.qemu_convert_options}")
print(f"OVA name: {args.ova_name}")
print(f"OVF template: {args.ovf_template}")
print(f"OVA output directory: {args.ova_outputdir}")
print(f"VMDK images: {args.vmdk_image}")

ovf_template_p = Path(args.ovf_template).absolute()
if not ovf_template_p.is_file():
    raise FileNotFoundError(args.ovf_template)
ovf_dir_p = ovf_template_p.parent.absolute()
if not ovf_dir_p.is_dir():
    raise FileNotFoundError(str(ovf_dir))

ova_output_p = Path(args.ova_outputdir).absolute()
if not ova_output_p.is_dir():
    raise FileNotFoundError(args.ova_outputdir)

assert isinstance(args.vmdk_image, list)
vmdk_image_dir_p = None
for vmdk_image in args.vmdk_image:
    vmdk_image_p = Path(vmdk_image).absolute()
    if not vmdk_image_p.is_file():
        raise FileNotFoundError(vmdk_image)
    if not vmdk_image_dir_p:
        vmdk_image_dir_p = vmdk_image_p.parent
    else:
        if vmdk_image_dir_p != vmdk_image_p.parent:
            raise RuntimeError("VMDK images must be in the same directory")

def convert_image(vmdk, vmdk_new, opts):
    q_args = ["qemu-img", "convert", "-f", "vmdk", "-O", "vmdk", vmdk, vmdk_new, "-o", opts]
    print("qemu convert command:", q_args)
    subprocess.check_call(q_args)

if qconv:
    print("Performing vmdk image conversions:")
    images = []
    for vmdk_image in args.vmdk_image:
        convert_image(vmdk_image, vmdk_image + ".converted.vmdk", args.qemu_convert_options)
        images.append(vmdk_image + ".converted.vmdk")
else:
    print("Skip VMDK conversion")
    images = args.vmdk_image

cmd = ["docker", "run", "-w", DOCKER_OVA_OUTPUTDIR]

mounts = [
    (str(ovf_dir_p), DOCKER_OVF_DIR),
    (str(vmdk_image_dir_p), DOCKER_VMDK_IMAGE_DIR),
    (str(ova_output_p), DOCKER_OVA_OUTPUTDIR),
]

for local_dir, docker_dir in mounts:
    cmd.append("--mount")
    cmd.append(f"type=bind,source={local_dir},destination={docker_dir}")

cmd.append(DOCKER_TAG_NAME)

# mkova.sh usage:
# /usr/bin/mkova.sh ova_name path_to_ovf_template disk1.vmdk [disk2.vmdk disk3.vmdk ...]
cmd.append("mkova.sh")

cmd.append(args.ova_name)
cmd.append(str(Path(DOCKER_OVF_DIR) / ovf_template_p.name))
for vmdk_image in images:
    cmd.append(str(Path(DOCKER_VMDK_IMAGE_DIR) / Path(vmdk_image).name))

print("Running:")
print(cmd)

subprocess.check_call(cmd)
