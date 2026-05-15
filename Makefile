.PHONY: deploy destroy reload ansible facts validate backup all

deploy:
	sudo clab deploy -t topology.clab.yml --reconfigure

destroy:
	sudo clab destroy -t topology.clab.yml --cleanup

reload: destroy deploy

ansible:
	cd ansible && ansible-galaxy collection install -r requirements.yml

facts: ansible
	cd ansible && ansible-playbook playbooks/00-gather-facts.yml -i inventory.yml

validate: ansible
	cd ansible && ansible-playbook playbooks/02-validate-network.yml -i inventory.yml

backup: ansible
	cd ansible && ansible-playbook playbooks/01-backup-configs.yml -i inventory.yml

ssh-spine01:
	ssh admin@172.20.0.11

ssh-leaf01:
	ssh admin@172.20.0.21

ssh-host01:
	ssh root@172.20.0.101

all: deploy ansible facts validate backup
