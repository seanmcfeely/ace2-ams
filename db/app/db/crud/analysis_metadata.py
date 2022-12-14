from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from db import crud
from api_models.analysis_metadata import AnalysisMetadataCreate
from api_models.metadata_critical_point import MetadataCriticalPointCreate
from api_models.metadata_detection_point import MetadataDetectionPointCreate
from api_models.metadata_directive import MetadataDirectiveCreate
from api_models.metadata_display_type import MetadataDisplayTypeCreate
from api_models.metadata_display_value import MetadataDisplayValueCreate
from api_models.metadata_sort import MetadataSortCreate
from api_models.metadata_tag import MetadataTagCreate
from api_models.metadata_time import MetadataTimeCreate
from db.schemas.analysis import Analysis
from db.schemas.analysis_metadata import AnalysisMetadata
from db.schemas.observable import Observable


def create_or_read(
    model: AnalysisMetadataCreate,
    db: Session,
    analysis: Optional[Analysis] = None,
    observable: Optional[Observable] = None,
) -> AnalysisMetadata:
    # Read the analysis and observable from the database if needed
    if not analysis:
        analysis = crud.analysis.read_by_uuid(uuid=model.analysis_uuid, db=db)
    if not observable:
        observable = crud.observable.read_by_uuid(uuid=model.observable_uuid, db=db)

    # Create or read the metadata object based on its type
    metadata_object = None

    if model.type == "critical_point":
        metadata_object = crud.metadata_critical_point.create_or_read(
            model=MetadataCriticalPointCreate(value=model.value), db=db
        )

    if model.type == "detection_point":
        metadata_object = crud.metadata_detection_point.create_or_read(
            model=MetadataDetectionPointCreate(value=model.value), db=db
        )

    elif model.type == "directive":
        metadata_object = crud.metadata_directive.create_or_read(
            model=MetadataDirectiveCreate(value=model.value), db=db
        )

    elif model.type == "display_type":
        metadata_object = crud.metadata_display_type.create_or_read(
            model=MetadataDisplayTypeCreate(value=model.value), db=db
        )

    elif model.type == "display_value":
        metadata_object = crud.metadata_display_value.create_or_read(
            model=MetadataDisplayValueCreate(value=model.value), db=db
        )

    elif model.type == "sort":
        metadata_object = crud.metadata_sort.create_or_read(model=MetadataSortCreate(value=model.value), db=db)

    elif model.type == "tag":
        metadata_object = crud.metadata_tag.create_or_read(model=MetadataTagCreate(value=model.value), db=db)

    elif model.type == "time":
        metadata_object = crud.metadata_time.create_or_read(model=MetadataTimeCreate(value=model.value), db=db)

    # Create the analysis metadata object
    if metadata_object:
        obj = AnalysisMetadata(
            analysis_uuid=analysis.uuid, observable_uuid=observable.uuid, metadata_uuid=metadata_object.uuid
        )

        if crud.helpers.create(obj=obj, db=db):
            # Refreshing the observable object ensures that its all_analysis_metadata relationship is updated
            db.refresh(observable)
            return obj

        return read_existing(
            analysis_uuid=analysis.uuid, observable_uuid=observable.uuid, metadata_uuid=metadata_object.uuid, db=db
        )


def read_existing(analysis_uuid: UUID, observable_uuid: UUID, metadata_uuid: UUID, db: Session) -> AnalysisMetadata:
    return (
        db.execute(
            select(AnalysisMetadata).where(
                AnalysisMetadata.analysis_uuid == analysis_uuid,
                AnalysisMetadata.observable_uuid == observable_uuid,
                AnalysisMetadata.metadata_uuid == metadata_uuid,
            )
        )
        .scalars()
        .one()
    )
