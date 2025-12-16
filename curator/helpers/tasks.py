"""Task management helpers for checking and managing OpenSearch running tasks"""

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Mapping of curator action names to OpenSearch task action patterns
# These are the task action strings that appear in _tasks API responses
CURATOR_TO_OPENSEARCH_TASK_ACTIONS: Dict[str, List[str]] = {
    'forcemerge': ['indices:admin/forcemerge'],
    'reindex': ['indices:data/write/reindex'],
    'shrink': ['indices:admin/shrink'],
    'split': ['indices:admin/split'],
    'clone': ['indices:admin/clone'],
    'snapshot': ['cluster:admin/snapshot/create'],
    'restore': ['cluster:admin/snapshot/restore'],
    'open': ['indices:admin/open'],
    'close': ['indices:admin/close'],
    'delete_indices': ['indices:admin/delete'],
    'rollover': ['indices:admin/rollover'],
}


def get_running_tasks(
    client,
    actions: Optional[List[str]] = None,
    detailed: bool = True,
) -> Dict:
    """
    Get currently running tasks from OpenSearch.

    :param client: OpenSearch client connection
    :param actions: Optional list of action patterns to filter tasks
    :param detailed: Whether to get detailed task information

    :type client: :py:class:`~.opensearchpy.OpenSearch`
    :type actions: list
    :type detailed: bool

    :returns: Dictionary of running tasks grouped by node
    :rtype: dict
    """
    params: Dict[str, Any] = {'detailed': detailed}
    if actions:
        params['actions'] = ','.join(actions)

    try:
        return client.tasks.list(**params)
    except Exception as err:
        logger.error('Failed to get running tasks: %s', err)
        raise


def get_tasks_for_action(client, curator_action: str) -> List[Dict]:
    """
    Get all running tasks that match a curator action type.

    :param client: OpenSearch client connection
    :param curator_action: The curator action name (e.g., 'forcemerge', 'reindex')

    :type client: :py:class:`~.opensearchpy.OpenSearch`
    :type curator_action: str

    :returns: List of matching task dictionaries
    :rtype: list
    """
    opensearch_actions = CURATOR_TO_OPENSEARCH_TASK_ACTIONS.get(curator_action, [])
    if not opensearch_actions:
        logger.warning(
            'No OpenSearch task action mapping found for curator action: %s',
            curator_action,
        )
        return []

    tasks_response = get_running_tasks(client, actions=opensearch_actions)
    matching_tasks = []

    # Extract tasks from the response
    # Response format: {"nodes": {"node_id": {"tasks": {"task_id": {...}}}}}
    nodes = tasks_response.get('nodes', {})
    for node_id, node_data in nodes.items():
        tasks = node_data.get('tasks', {})
        for task_id, task_data in tasks.items():
            task_info = {'task_id': task_id, 'node_id': node_id, **task_data}
            matching_tasks.append(task_info)

    return matching_tasks


def get_tasks_for_indices(
    client, curator_action: str, indices: List[str]
) -> List[Dict]:
    """
    Get running tasks for a specific curator action that affect any of the given indices.

    :param client: OpenSearch client connection
    :param curator_action: The curator action name
    :param indices: List of index names to check

    :type client: :py:class:`~.opensearchpy.OpenSearch`
    :type curator_action: str
    :type indices: list

    :returns: List of matching task dictionaries that affect the specified indices
    :rtype: list
    """
    all_tasks = get_tasks_for_action(client, curator_action)
    if not all_tasks:
        return []

    indices_set = set(indices)
    matching_tasks = []

    for task in all_tasks:
        # The 'description' field typically contains the index info
        # e.g., "forcemerge[index1,index2]" or "reindex from [source] to [dest]"
        description = task.get('description', '')

        # Check if any of our indices appear in the task description
        for idx in indices_set:
            if idx in description:
                matching_tasks.append(task)
                break

    return matching_tasks


def is_action_running(client, curator_action: str) -> bool:
    """
    Check if there are any running tasks for a specific curator action.

    :param client: OpenSearch client connection
    :param curator_action: The curator action name

    :type client: :py:class:`~.opensearchpy.OpenSearch`
    :type curator_action: str

    :returns: True if there are running tasks for this action
    :rtype: bool
    """
    tasks = get_tasks_for_action(client, curator_action)
    return len(tasks) > 0


def is_action_running_for_indices(
    client, curator_action: str, indices: List[str]
) -> bool:
    """
    Check if there are running tasks for a specific action affecting given indices.

    :param client: OpenSearch client connection
    :param curator_action: The curator action name
    :param indices: List of index names to check

    :type client: :py:class:`~.opensearchpy.OpenSearch`
    :type curator_action: str
    :type indices: list

    :returns: True if there are running tasks affecting the specified indices
    :rtype: bool
    """
    tasks = get_tasks_for_indices(client, curator_action, indices)
    return len(tasks) > 0


def get_conflicting_indices(
    client, curator_action: str, indices: List[str]
) -> Set[str]:
    """
    Get the subset of indices that have running tasks for the specified action.

    :param client: OpenSearch client connection
    :param curator_action: The curator action name
    :param indices: List of index names to check

    :type client: :py:class:`~.opensearchpy.OpenSearch`
    :type curator_action: str
    :type indices: list

    :returns: Set of index names that have running tasks
    :rtype: set
    """
    tasks = get_tasks_for_indices(client, curator_action, indices)
    if not tasks:
        return set()

    indices_set = set(indices)
    conflicting = set()

    for task in tasks:
        description = task.get('description', '')
        for idx in indices_set:
            if idx in description:
                conflicting.add(idx)

    return conflicting


def format_running_tasks(tasks: List[Dict]) -> str:
    """
    Format running tasks into a human-readable string.

    :param tasks: List of task dictionaries

    :type tasks: list

    :returns: Formatted string describing the running tasks
    :rtype: str
    """
    if not tasks:
        return "No running tasks found"

    lines = []
    for task in tasks:
        task_id = task.get('task_id', 'unknown')
        action = task.get('action', 'unknown')
        description = task.get('description', 'N/A')
        running_time_nanos = task.get('running_time_in_nanos', 0)
        running_time_secs = running_time_nanos / 1_000_000_000

        lines.append(
            f"  - Task {task_id}: {action} "
            f"(running for {running_time_secs:.1f}s) - {description}"
        )

    return "\n".join(lines)
