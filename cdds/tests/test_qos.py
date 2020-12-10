import pytest

from cdds.core import Qos, Policy
from cdds.util.time import duration


def test_all_qos():
    qos = Qos()
    qos += Policy.Reliability.BestEffort(duration(weeks=2))
    qos += Policy.Durability.Persistent
    qos += Policy.History.KeepLast(12)
    qos += Policy.ResourceLimits(max_samples=10, max_instances=100, max_samples_per_instance=12)
    qos += Policy.PresentationAccessScope.Group(coherent_access=True, ordered_access=False)
    qos += Policy.Lifespan(duration(nanoseconds=12, hours=2))
    qos += Policy.Deadline(duration(minutes=1.2))
    qos += Policy.LatencyBudget(duration(seconds=12))
    qos += Policy.Ownership.Exclusive
    qos += Policy.OwnershipStrength(12)
    qos += Policy.Liveliness.Automatic(duration(microseconds=42))
    qos += Policy.TimeBasedFilter(duration(weeks=21))
    qos += Policy.Partitions("No", "Way", "Man!")
    qos += Policy.TransportPriority(3)
    qos += Policy.DestinationOrder.BySourceTimestamp
    qos += Policy.WriterDataLifecycle(autodispose=True)
    qos += Policy.ReaderDataLifecycle(9, 8)
    qos += Policy.DurabilityService(12, Policy.History.KeepAll, 4, 2, 3)
    qos += Policy.IgnoreLocal.Participant

    assert qos.get_reliability() == Policy.Reliability.BestEffort(duration(weeks=2))
    assert qos.get_durability() == Policy.Durability.Persistent
    assert qos.get_history() == Policy.History.KeepLast(12)
    assert qos.get_resource_limits() == Policy.ResourceLimits(max_samples=10, max_instances=100, max_samples_per_instance=12)
    assert qos.get_presentation_access_scope() == Policy.PresentationAccessScope.Group(coherent_access=True, ordered_access=False)
    assert qos.get_lifespan() == Policy.Lifespan(duration(nanoseconds=12, hours=2))
    assert qos.get_deadline() == Policy.Deadline(duration(minutes=1.2))
    assert qos.get_latency_budget() == Policy.LatencyBudget(duration(seconds=12))
    assert qos.get_ownership() == Policy.Ownership.Exclusive
    assert qos.get_ownership_strength() == Policy.OwnershipStrength(12)
    assert qos.get_liveliness() == Policy.Liveliness.Automatic(duration(microseconds=42))
    assert qos.get_time_based_filter() == Policy.TimeBasedFilter(duration(weeks=21))
    assert qos.get_partitions() == Policy.Partitions("No", "Way", "Man!")
    assert qos.get_transport_priority() == Policy.TransportPriority(3)
    assert qos.get_destination_order() == Policy.DestinationOrder.BySourceTimestamp
    assert qos.get_writer_data_lifecycle() == Policy.WriterDataLifecycle(autodispose=True)
    assert qos.get_reader_data_lifecycle() == Policy.ReaderDataLifecycle(9, 8)
    assert qos.get_durability_service() == Policy.DurabilityService(12, Policy.History.KeepAll, 4, 2, 3)
    assert qos.get_ignore_local() == Policy.IgnoreLocal.Participant