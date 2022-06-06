
##############################################################
### Configure Backend Remote State and Providers
##############################################################

terraform {
  backend "remote" {
    hostname     = "app.terraform.io"
    organization = "FifthThird"
    workspaces {
      prefix = "idr-aws-ice2-module-filetype-dev"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

module "filetype_analysis_module" {
  source = "git@github.info53.com:Fifth-Third/terraform-aws-idr-analysis-module.git"
  #Vars
  environment              = var.environment
  analysis_module_name     = var.analysis_module_name
  analysis_ecr_image       = var.analysis_ecr_image
  analysis_lambda_env_vars = var.analysis_lambda_env_vars
}
