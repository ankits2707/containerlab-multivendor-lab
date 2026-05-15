#!/usr/bin/env python3
"""
Containerlab Multi-Vendor Automation Lab
Deploy, configure, and test with your existing images:
  - Arista cEOS 4.32.2F (spines)
  - Cisco IOL 17.12.01 (leaf routers)
  - Cisco IOL L2 17.12.01 (edge switch)
  - network-multitool (linux hosts)

Usage:
    python deploy.py deploy       # deploy lab
    python deploy.py destroy      # tear down
    python deploy.py ansible      # install collections + test connectivity
    python deploy.py all          # deploy + ansible + run playbooks
"""

import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
ANSIBLE_DIR = os.path.join(ROOT, "ansible")
TOPO_FILE = os.path.join(ROOT, "topology.clab.yml")


def run(cmd, cwd=ROOT):
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True)
    if result.returncode != 0:
        print(f"Command failed (rc={result.returncode})")
        sys.exit(result.returncode)
    return result


def deploy():
    print("=" * 60)
    print(" Deploying Containerlab topology")
    print("=" * 60)
    run(f"sudo clab deploy -t {TOPO_FILE} --reconfigure")
    print("\nDone! Nodes are booting. Check with: sudo clab inspect")


def destroy():
    print("=" * 60)
    print(" Destroying Containerlab topology")
    print("=" * 60)
    run(f"sudo clab destroy -t {TOPO_FILE} --cleanup")


def ansible_setup():
    print("=" * 60)
    print(" Installing Ansible collections")
    print("=" * 60)
    run("ansible-galaxy collection install -r requirements.yml", cwd=ANSIBLE_DIR)

    print("\n Testing connectivity to all nodes...")
    run("ansible all -i inventory.yml -m ping -o", cwd=ANSIBLE_DIR)


def run_all():
    deploy()
    ansible_setup()

    print("\n" + "=" * 60)
    print(" Gathering facts from all devices")
    print("=" * 60)
    run("ansible-playbook playbooks/00-gather-facts.yml -i inventory.yml", cwd=ANSIBLE_DIR)

    print("\n" + "=" * 60)
    print(" Validating network state")
    print("=" * 60)
    run("ansible-playbook playbooks/02-validate-network.yml -i inventory.yml", cwd=ANSIBLE_DIR)

    print("\n" + "=" * 60)
    print(" Backing up device configs")
    print("=" * 60)
    run("ansible-playbook playbooks/01-backup-configs.yml -i inventory.yml", cwd=ANSIBLE_DIR)

    print("\n" + "=" * 60)
    print(" All done!")
    print("=" * 60)
    print("  Arista spines:  ssh admin@172.20.0.11 (eAPI on port 80)")
    print("  Cisco leafs:    ssh admin@172.20.0.21")
    print("  Edge switch:    ssh admin@172.20.0.30")
    print("  Hosts:          ssh root@172.20.0.101")
    print()
    print("  Ansible inventory: ansible/inventory.yml")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Containerlab multivendor lab manager")
    parser.add_argument("action", nargs="?", default="all",
                        choices=["deploy", "destroy", "ansible", "all"])
    args = parser.parse_args()

    actions = {
        "deploy": deploy,
        "destroy": destroy,
        "ansible": ansible_setup,
        "all": run_all,
    }
    actions[args.action]()
